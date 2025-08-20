import re
import time
import random

import requests
import shutil
import logging
import os
from frictionless import Package, system
from pathlib import Path
from urllib.parse import urlparse
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .config import get_rate_limit_config, get_github_config

logger = logging.getLogger(__name__)

class GitHubRateLimitHandler:
    """Handler para lidar com rate limiting do GitHub API"""
    
    def __init__(self, max_retries=None, base_delay=None, max_delay=None):
        config = get_rate_limit_config()
        self.max_retries = max_retries or config["max_retries"]
        self.base_delay = base_delay or config["base_delay"]
        self.max_delay = max_delay or config["max_delay"]
    
    def should_retry(self, response):
        """Verifica se deve tentar novamente baseado na resposta"""
        if response.status_code == 429:
            return True
        if response.status_code >= 500:
            return True
        return False
    
    def get_retry_after(self, response):
        """Extrai o tempo de espera do header Retry-After"""
        retry_after = response.headers.get('Retry-After')
        if retry_after:
            try:
                return int(retry_after)
            except ValueError:
                pass
        return None
    
    def get_github_rate_limit_info(self, response):
        """Extrai informações de rate limiting do GitHub"""
        remaining = response.headers.get('X-RateLimit-Remaining')
        reset_time = response.headers.get('X-RateLimit-Reset')
        
        if remaining is not None:
            remaining = int(remaining)
        if reset_time is not None:
            reset_time = int(reset_time)
            
        return remaining, reset_time
    
    def calculate_delay(self, attempt, retry_after=None):
        """Calcula o delay para o próximo retry"""
        if retry_after:
            return retry_after
        
        # Backoff exponencial com jitter
        delay = min(self.base_delay * (2 ** attempt) + random.uniform(0, 1), self.max_delay)
        return delay
    
    def handle_rate_limit(self, response, attempt):
        """Trata rate limiting e retorna delay apropriado"""
        if response.status_code == 429:
            retry_after = self.get_retry_after(response)
            remaining, reset_time = self.get_github_rate_limit_info(response)
            
            if remaining == 0 and reset_time:
                wait_time = reset_time - int(time.time()) + 1
                if wait_time > 0:
                    logger.warning(f'Rate limit atingido. Aguardando {wait_time} segundos até reset...')
                    return wait_time
            
            if retry_after:
                logger.warning(f'Rate limit atingido. Aguardando {retry_after} segundos...')
                return retry_after
            
            delay = self.calculate_delay(attempt)
            logger.warning(f'Rate limit atingido. Aguardando {delay:.1f} segundos...')
            return delay
        
        return self.calculate_delay(attempt)

def create_retry_session(max_retries=None, backoff_factor=None, status_forcelist=None):
    """Cria uma sessão com retry automático"""
    config = get_rate_limit_config()
    
    max_retries = max_retries or config["max_retries"]
    backoff_factor = backoff_factor or config["backoff_factor"]
    status_forcelist = status_forcelist or config["status_forcelist"]
    
    session = requests.Session()
    
    retry_strategy = Retry(
        total=max_retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        allowed_methods=["HEAD", "GET", "OPTIONS"]
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    return session

def make_request_with_retry(session, url, headers=None, stream=False, rate_limit_handler=None):
    """Faz uma requisição com retry e tratamento de rate limiting"""
    if rate_limit_handler is None:
        rate_limit_handler = GitHubRateLimitHandler()
    
    for attempt in range(rate_limit_handler.max_retries + 1):
        try:
            response = session.get(url, headers=headers, stream=stream)
            
            if response.status_code == 200:
                return response
            
            if rate_limit_handler.should_retry(response) and attempt < rate_limit_handler.max_retries:
                delay = rate_limit_handler.handle_rate_limit(response, attempt)
                logger.info(f'Tentativa {attempt + 1} falhou. Aguardando {delay:.1f} segundos...')
                time.sleep(delay)
                continue
            
            response.raise_for_status()
            
        except requests.exceptions.RequestException as e:
            if attempt < rate_limit_handler.max_retries:
                delay = rate_limit_handler.calculate_delay(attempt)
                logger.warning(f'Erro na requisição (tentativa {attempt + 1}): {e}. Aguardando {delay:.1f} segundos...')
                time.sleep(delay)
                continue
            raise
    
    # Se chegou aqui, todas as tentativas falharam
    raise requests.exceptions.RequestException(f"Falha após {rate_limit_handler.max_retries + 1} tentativas")

def update_session_headers(session, source):
    """Atualiza headers da sessão com autenticação se necessário"""
    varenv_name = source.get('token', None)
    if varenv_name:
        logger.info(f'Using token stored in {varenv_name} for accessing data package {source["name"]}')
        token = os.getenv(varenv_name)
        if token:
            session.headers['Authorization'] = f"Bearer {token}"
        else:
            logger.warning(f'Token {varenv_name} não encontrado nas variáveis de ambiente')
    
    # Adiciona User-Agent para melhor identificação
    github_config = get_github_config()
    session.headers['User-Agent'] = github_config['user_agent']
    
    return session

def extract_source_packages(toml_package, output_dir):
    for key, source in toml_package["packages"].items():
        source["name"] = key
        logger.info(f'Downloading package {source["name"]}....')
        extract_source_package(source, output_dir)

def extract_source_package(source, output_dir):
    """Extrai um pacote fonte com tratamento robusto de rate limiting"""
    
    # Valida a URL antes de processar
    path = source["path"]
    if path.startswith("https://raw.githubusercontent.com/"):
        # Valida formato da URL do GitHub
        try:
            parsed_url = urlparse(path)
            path_parts = parsed_url.path.strip('/').split('/')
            
            if len(path_parts) < 3:
                raise ValueError(f"URL inválida do GitHub: {path}. Formato esperado: user/repo/ref/datapackage.json")
            
            if not path.endswith('datapackage.json'):
                logger.warning(f'URL não termina com datapackage.json: {path}')
                
        except Exception as e:
            logger.error(f'Erro na validação da URL do pacote "{source["name"]}": {e}')
            raise
    
    # Cria sessão com retry automático
    session = create_retry_session()
    
    # Atualiza headers da sessão
    session = update_session_headers(session, source)
    
    # Cria handler para rate limiting
    rate_limit_handler = GitHubRateLimitHandler()
    
    try:
        with system.use_context(http_session=session):
            package = Package(source["path"])
        
        package_descriptor_path = Path(output_dir, source["name"], 'datapackage.json')
        package.dereference()
        
        fetch_resources = source.get('resources', package.resource_names)
        
        for res in [res for res in package.resource_names if res not in fetch_resources]:
            package.remove_resource(res)
        
        # Se for uma URL do GitHub, obtém informações do commit
        if urlparse(source['path']).netloc in {'github.com', 'raw.githubusercontent.com'}:
            try:
                commit_info = get_commit_info(source, rate_limit_handler)
                package.custom.update({'remote': commit_info})
            except Exception as e:
                logger.warning(f'Não foi possível obter informações do commit: {e}')
        
        package.to_json(package_descriptor_path)
        
        if package.resources == []:
            logger.warning(f'All resources were not found for package "{source["name"]}". '
                           f'Please check your data.toml file.')
            return
        
        # Download dos recursos com retry
        for resource_name in fetch_resources:
            if resource_name in package.resource_names:
                try:
                    resource = package.get_resource(resource_name)
                    resource_remotepath = f'{resource.basepath}/{resource.path}'
                    
                    # Usa função com retry para download
                    response = make_request_with_retry(
                        session, 
                        str(resource_remotepath), 
                        stream=True, 
                        rate_limit_handler=rate_limit_handler
                    )
                    
                    resource_path = Path(package_descriptor_path.parent, resource.path)
                    resource_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    if 'text' in resource.mediatype:
                        response.raw.decode_content = True
                    else:
                        response.raw.decode_content = False
                    
                    with open(resource_path, 'wb') as file:
                        shutil.copyfileobj(response.raw, file)
                    
                    logger.info(f'Data file of resource "{resource.name}" saved in "{resource_path}"')
                    
                except Exception as e:
                    logger.error(f'Erro ao baixar recurso "{resource_name}": {e}')
                    continue
            else:
                logger.warning(f'Resource "{resource_name}" not found for package "{package.name}". '
                            f'Please check your `data.toml` file.')
    
    except Exception as e:
        # Verifica se é um erro específico de URL inválida
        if "URL inválida do GitHub" in str(e):
            logger.error(f'Erro na URL do pacote "{source["name"]}": {e}')
            logger.error(f'URL fornecida: {source["path"]}')
            logger.error('Formato esperado: https://raw.githubusercontent.com/user/repo/ref/datapackage.json')
        elif "404 Client Error" in str(e):
            logger.error(f'Pacote "{source["name"]}" não encontrado na URL: {source["path"]}')
            logger.error('Verifique se:')
            logger.error('1. A URL está correta')
            logger.error('2. O repositório existe')
            logger.error('3. O arquivo datapackage.json existe no caminho especificado')
        else:
            logger.error(f'Erro ao processar pacote "{source["name"]}": {e}')
        raise

def get_commit_info(source, rate_limit_handler=None):
    """Obtém informações do commit com tratamento de rate limiting"""
    
    # Extrai detalhes do repositório da URL
    parsed_url = parse_rawgithub_url(source["path"])
    
    # Configura headers para autenticação
    varenv_name = source.get('token', None)
    if varenv_name:
        token = os.getenv(varenv_name)
        if token:
            headers = {
                "Authorization": f"token {token}",
                "User-Agent": get_github_config()['user_agent']
            }
        else:
            logger.warning(f'Token {varenv_name} não encontrado')
            headers = {"User-Agent": get_github_config()['user_agent']}
    else:
        headers = {"User-Agent": get_github_config()['user_agent']}
    
    # GitHub API URL para obter o hash do commit
    github_endpoint = "commits" if is_commit_sha(parsed_url['ref']) else "branches"
    api_url = f"https://api.github.com/repos/{parsed_url['user']}/{parsed_url['repo']}/{github_endpoint}/{parsed_url['ref']}"
    
    # Cria sessão com retry
    session = create_retry_session()
    
    try:
        # Usa função com retry para a requisição da API
        response = make_request_with_retry(
            session, 
            api_url, 
            headers=headers, 
            rate_limit_handler=rate_limit_handler
        )
        
        data = response.json()
        
        return {
            "host": parsed_url['host'],
            "user": parsed_url['user'],
            "repo": parsed_url['repo'],
            "ref": parsed_url['ref'],
            "sha": data['sha'] if github_endpoint == 'commits' else data['commit']['sha']
        }
        
    except Exception as e:
        logger.error(f'Erro ao obter informações do commit: {e}')
        raise


def parse_rawgithub_url(url):
    """
    Returns the parts of a github url in a dict
    Handles both raw.githubusercontent.com and github.com URLs
    """
    parsed_url = urlparse(url)
    path_parts = parsed_url.path.strip('/').split('/')
    
    # Remove o nome do arquivo se presente (ex: datapackage.json)
    if len(path_parts) > 3 and '.' in path_parts[-1]:
        path_parts = path_parts[:-1]
    
    # Garante que temos pelo menos 3 partes: user/repo/ref
    if len(path_parts) < 3:
        raise ValueError(f"URL inválida do GitHub: {url}. Formato esperado: user/repo/ref[/file]")
    
    return dict(
        host=parsed_url.netloc,
        user=path_parts[0],
        repo=path_parts[1],
        ref=path_parts[2],
    )


def is_commit_sha(ref):
    """
    Returns True if ref is a valid commit SHA
    """
    if re.match(r"([a-z0-9]{40})", ref):
        return True
    else:
        return False
