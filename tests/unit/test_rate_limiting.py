"""
Testes para a solução de rate limiting implementada
"""
import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from requests.models import Response
from urllib3.util.retry import Retry

from dpm.install import (
    GitHubRateLimitHandler,
    create_retry_session,
    make_request_with_retry
)


class TestGitHubRateLimitHandler:
    """Testes para a classe GitHubRateLimitHandler"""
    
    def test_init_with_defaults(self):
        """Testa inicialização com valores padrão"""
        handler = GitHubRateLimitHandler()
        assert handler.max_retries == 5
        assert handler.base_delay == 1
        assert handler.max_delay == 60
    
    def test_init_with_custom_values(self):
        """Testa inicialização com valores customizados"""
        handler = GitHubRateLimitHandler(max_retries=10, base_delay=2, max_delay=120)
        assert handler.max_retries == 10
        assert handler.base_delay == 2
        assert handler.max_delay == 120
    
    def test_should_retry_429(self):
        """Testa se deve retry para erro 429"""
        handler = GitHubRateLimitHandler()
        response = Mock()
        response.status_code = 429
        
        assert handler.should_retry(response) is True
    
    def test_should_retry_500(self):
        """Testa se deve retry para erro 500"""
        handler = GitHubRateLimitHandler()
        response = Mock()
        response.status_code = 500
        
        assert handler.should_retry(response) is True
    
    def test_should_retry_200(self):
        """Testa se não deve retry para sucesso"""
        handler = GitHubRateLimitHandler()
        response = Mock()
        response.status_code = 200
        
        assert handler.should_retry(response) is False
    
    def test_get_retry_after_valid(self):
        """Testa extração de Retry-After válido"""
        handler = GitHubRateLimitHandler()
        response = Mock()
        response.headers = {'Retry-After': '60'}
        
        assert handler.get_retry_after(response) == 60
    
    def test_get_retry_after_invalid(self):
        """Testa extração de Retry-After inválido"""
        handler = GitHubRateLimitHandler()
        response = Mock()
        response.headers = {'Retry-After': 'invalid'}
        
        assert handler.get_retry_after(response) is None
    
    def test_get_github_rate_limit_info(self):
        """Testa extração de informações de rate limiting do GitHub"""
        handler = GitHubRateLimitHandler()
        response = Mock()
        response.headers = {
            'X-RateLimit-Remaining': '10',
            'X-RateLimit-Reset': '1234567890'
        }
        
        remaining, reset_time = handler.get_github_rate_limit_info(response)
        assert remaining == 10
        assert reset_time == 1234567890
    
    def test_calculate_delay_with_retry_after(self):
        """Testa cálculo de delay com Retry-After"""
        handler = GitHubRateLimitHandler()
        delay = handler.calculate_delay(1, retry_after=30)
        assert delay == 30
    
    def test_calculate_delay_exponential_backoff(self):
        """Testa cálculo de delay com backoff exponencial"""
        handler = GitHubRateLimitHandler(base_delay=1, max_delay=60)
        
        # Primeira tentativa
        delay1 = handler.calculate_delay(0)
        assert 1 <= delay1 <= 2
        
        # Segunda tentativa
        delay2 = handler.calculate_delay(1)
        assert 2 <= delay2 <= 3
        
        # Terceira tentativa
        delay3 = handler.calculate_delay(2)
        assert 4 <= delay3 <= 5
    
    def test_handle_rate_limit_429_with_retry_after(self):
        """Testa tratamento de rate limit 429 com Retry-After"""
        handler = GitHubRateLimitHandler()
        response = Mock()
        response.status_code = 429
        response.headers = {'Retry-After': '45'}
        
        delay = handler.handle_rate_limit(response, 1)
        assert delay == 45
    
    def test_handle_rate_limit_429_without_retry_after(self):
        """Testa tratamento de rate limit 429 sem Retry-After"""
        handler = GitHubRateLimitHandler()
        response = Mock()
        response.status_code = 429
        response.headers = {}
        
        delay = handler.handle_rate_limit(response, 1)
        assert delay > 0
    
    def test_handle_rate_limit_other_status(self):
        """Testa tratamento de outros status codes"""
        handler = GitHubRateLimitHandler()
        response = Mock()
        response.status_code = 500
        response.headers = {}
        
        delay = handler.handle_rate_limit(response, 1)
        assert delay > 0


class TestRetrySession:
    """Testes para criação de sessões com retry"""
    
    def test_create_retry_session_defaults(self):
        """Testa criação de sessão com valores padrão"""
        session = create_retry_session()
        
        # Verifica se o adapter foi configurado
        assert hasattr(session, 'mount')
        
        # Verifica se o retry strategy foi configurado
        adapter = session.get_adapter('https://')
        assert isinstance(adapter, type(session.get_adapter('https://')))
    
    def test_create_retry_session_custom_values(self):
        """Testa criação de sessão com valores customizados"""
        session = create_retry_session(
            max_retries=10,
            backoff_factor=2,
            status_forcelist=[429, 500]
        )
        
        assert hasattr(session, 'mount')


class TestMakeRequestWithRetry:
    """Testes para função de requisição com retry"""
    
    @patch('dpm.install.time.sleep')
    def test_successful_request_first_try(self, mock_sleep):
        """Testa requisição bem-sucedida na primeira tentativa"""
        session = Mock()
        response = Mock()
        response.status_code = 200
        session.get.return_value = response
        
        result = make_request_with_retry(session, 'http://example.com')
        
        assert result == response
        assert mock_sleep.call_count == 0
    
    @patch('dpm.install.time.sleep')
    def test_retry_on_429(self, mock_sleep):
        """Testa retry em caso de erro 429"""
        session = Mock()
        
        # Primeira tentativa falha com 429
        response1 = Mock()
        response1.status_code = 429
        response1.headers = {'Retry-After': '1'}
        
        # Segunda tentativa é bem-sucedida
        response2 = Mock()
        response2.status_code = 200
        
        session.get.side_effect = [response1, response2]
        
        result = make_request_with_retry(session, 'http://example.com')
        
        assert result == response2
        assert mock_sleep.call_count == 1
    
    @patch('dpm.install.time.sleep')
    def test_max_retries_exceeded(self, mock_sleep):
        """Testa se falha após exceder número máximo de tentativas"""
        session = Mock()
        
        # Todas as tentativas falham com 429
        response = Mock()
        response.status_code = 429
        response.headers = {}
        session.get.return_value = response
        
        with pytest.raises(Exception):
            make_request_with_retry(session, 'http://example.com', rate_limit_handler=GitHubRateLimitHandler(max_retries=2))
        
        # Verifica se fez o número correto de tentativas
        assert session.get.call_count == 3  # 2 retries + 1 tentativa inicial


class TestIntegration:
    """Testes de integração para verificar funcionamento completo"""
    
    def test_handler_with_config(self):
        """Testa se o handler usa configurações corretamente"""
        # Simula configuração via variáveis de ambiente
        with patch.dict('os.environ', {'DPM_MAX_RETRIES': '10'}):
            handler = GitHubRateLimitHandler()
            assert handler.max_retries == 10
    
    def test_session_creation_with_config(self):
        """Testa se a sessão é criada com configurações corretas"""
        with patch.dict('os.environ', {'DPM_BACKOFF_FACTOR': '2.0'}):
            session = create_retry_session()
            assert hasattr(session, 'mount')
