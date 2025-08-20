"""
Testes para a função parse_rawgithub_url corrigida
"""
import pytest
from dpm.install import parse_rawgithub_url


class TestParseRawGitHubURL:
    """Testes para a função parse_rawgithub_url"""
    
    def test_valid_raw_github_url(self):
        """Testa URL válida do raw.githubusercontent.com"""
        url = "https://raw.githubusercontent.com/splor-mg/dados-link-obz-2026/main/datapackage.json"
        result = parse_rawgithub_url(url)
        
        assert result["host"] == "raw.githubusercontent.com"
        assert result["user"] == "splor-mg"
        assert result["repo"] == "dados-link-obz-2026"
        assert result["ref"] == "main"
    
    def test_valid_github_url(self):
        """Testa URL válida do github.com"""
        url = "https://github.com/splor-mg/dados-link-obz-2026/blob/main/datapackage.json"
        result = parse_rawgithub_url(url)
        
        assert result["host"] == "github.com"
        assert result["user"] == "splor-mg"
        assert result["repo"] == "dados-link-obz-2026"
        assert result["ref"] == "main"
    
    def test_url_without_file(self):
        """Testa URL sem nome de arquivo"""
        url = "https://raw.githubusercontent.com/splor-mg/dados-link-obz-2026/main/"
        result = parse_rawgithub_url(url)
        
        assert result["host"] == "raw.githubusercontent.com"
        assert result["user"] == "splor-mg"
        assert result["repo"] == "dados-link-obz-2026"
        assert result["ref"] == "main"
    
    def test_url_with_commit_sha(self):
        """Testa URL com SHA de commit"""
        url = "https://raw.githubusercontent.com/splor-mg/dados-link-obz-2026/abc123def456/datapackage.json"
        result = parse_rawgithub_url(url)
        
        assert result["host"] == "raw.githubusercontent.com"
        assert result["user"] == "splor-mg"
        assert result["repo"] == "dados-link-obz-2026"
        assert result["ref"] == "abc123def456"
    
    def test_invalid_url_too_few_parts(self):
        """Testa URL inválida com poucas partes"""
        url = "https://raw.githubusercontent.com/splor-mg/datapackage.json"
        
        with pytest.raises(ValueError, match="URL inválida do GitHub"):
            parse_rawgithub_url(url)
    
    def test_invalid_url_missing_parts(self):
        """Testa URL inválida com partes faltando"""
        url = "https://raw.githubusercontent.com/splor-mg/"
        
        with pytest.raises(ValueError, match="URL inválida do GitHub"):
            parse_rawgithub_url(url)
    
    def test_url_with_multiple_file_extensions(self):
        """Testa URL com múltiplas extensões de arquivo"""
        url = "https://raw.githubusercontent.com/splor-mg/dados-link-obz-2026/main/data/file.csv.gz"
        result = parse_rawgithub_url(url)
        
        assert result["host"] == "raw.githubusercontent.com"
        assert result["user"] == "splor-mg"
        assert result["repo"] == "dados-link-obz-2026"
        assert result["ref"] == "main"
