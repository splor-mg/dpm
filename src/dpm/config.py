"""
Configurações para o DPM Data Package Manager
"""
import os
from typing import Dict, Any

# Configurações padrão para rate limiting e retry
DEFAULT_CONFIG = {
    "rate_limiting": {
        "max_retries": 5,
        "base_delay": 1,
        "max_delay": 60,
        "backoff_factor": 1,
        "status_forcelist": [429, 500, 502, 503, 504]
    },
    "github": {
        "user_agent": "dpm-data-package-manager/1.0",
        "timeout": 30
    },
    "logging": {
        "level": "INFO",
        "format": "%(asctime)s %(levelname)-5.5s [%(name)s] %(message)s"
    }
}

def get_config() -> Dict[str, Any]:
    """
    Obtém configuração do sistema, permitindo sobrescrever via variáveis de ambiente
    """
    config = DEFAULT_CONFIG.copy()
    
    # Permite sobrescrever configurações via variáveis de ambiente
    env_mappings = {
        "DPM_MAX_RETRIES": ("rate_limiting", "max_retries", int),
        "DPM_BASE_DELAY": ("rate_limiting", "base_delay", float),
        "DPM_MAX_DELAY": ("rate_limiting", "max_delay", int),
        "DPM_BACKOFF_FACTOR": ("rate_limiting", "backoff_factor", float),
        "DPM_TIMEOUT": ("github", "timeout", int),
        "DPM_LOG_LEVEL": ("logging", "level", str),
    }
    
    for env_var, (section, key, type_converter) in env_mappings.items():
        env_value = os.getenv(env_var)
        if env_value is not None:
            try:
                config[section][key] = type_converter(env_value)
            except (ValueError, TypeError):
                # Se não conseguir converter, mantém o valor padrão
                pass
    
    return config

def get_rate_limit_config() -> Dict[str, Any]:
    """Obtém configurações específicas para rate limiting"""
    return get_config()["rate_limiting"]

def get_github_config() -> Dict[str, Any]:
    """Obtém configurações específicas para GitHub"""
    return get_config()["github"]

def get_logging_config() -> Dict[str, Any]:
    """Obtém configurações específicas para logging"""
    return get_config()["logging"]
