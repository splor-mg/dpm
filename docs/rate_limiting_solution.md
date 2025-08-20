# Solução para Rate Limiting HTTP 429

## Problema Identificado

O issue [#184](https://github.com/splor-mg/atividades/issues/184) relatou um erro HTTP 429 (Too Many Requests) ao tentar acessar o GitHub através do comando `dpm install`. Este erro ocorre quando o GitHub API atinge o limite de requisições permitidas.

## Solução Implementada

### 1. Retry com Backoff Exponencial

Implementamos um sistema robusto de retry que:
- Detecta automaticamente erros HTTP 429
- Implementa backoff exponencial com jitter para evitar thundering herd
- Respeita os headers `Retry-After` do GitHub
- Monitora os headers de rate limiting (`X-RateLimit-Remaining`, `X-RateLimit-Reset`)

### 2. Classe GitHubRateLimitHandler

```python
class GitHubRateLimitHandler:
    """Handler para lidar com rate limiting do GitHub API"""
    
    def __init__(self, max_retries=None, base_delay=None, max_delay=None):
        # Configurações configuráveis via variáveis de ambiente
        pass
    
    def handle_rate_limit(self, response, attempt):
        # Trata rate limiting inteligentemente
        pass
```

### 3. Sessões com Retry Automático

```python
def create_retry_session(max_retries=None, backoff_factor=None, status_forcelist=None):
    """Cria uma sessão com retry automático"""
    # Usa urllib3.util.Retry para retry automático
    pass
```

### 4. Configuração Flexível

As configurações podem ser personalizadas via variáveis de ambiente:

```bash
# Número máximo de tentativas
export DPM_MAX_RETRIES=10

# Delay base entre tentativas (em segundos)
export DPM_BASE_DELAY=2

# Delay máximo entre tentativas (em segundos)
export DPM_MAX_DELAY=120

# Fator de backoff exponencial
export DPM_BACKOFF_FACTOR=1.5

# Timeout para requisições (em segundos)
export DPM_TIMEOUT=60

# Nível de logging
export DPM_LOG_LEVEL=DEBUG
```

## Como Funciona

### 1. Detecção de Rate Limiting

Quando uma requisição retorna HTTP 429:
- O sistema verifica o header `Retry-After` para saber quanto tempo esperar
- Se não houver `Retry-After`, calcula um delay baseado no número da tentativa
- Monitora os headers `X-RateLimit-Remaining` e `X-RateLimit-Reset`

### 2. Estratégia de Retry

```python
# Exemplo de backoff exponencial com jitter
delay = min(base_delay * (2 ** attempt) + random.uniform(0, 1), max_delay)
```

### 3. Logging Inteligente

O sistema fornece logs detalhados sobre:
- Tentativas de retry
- Tempos de espera
- Informações de rate limiting
- Erros e sucessos

## Exemplo de Uso

### Configuração Básica

```toml
# data.toml
[packages.obz_2026]
path = "https://raw.githubusercontent.com/splor-mg/dados-obz-2026/main/datapackage.json"
token = "GITHUB_PAT"
```

### Execução

```bash
# Com configurações padrão
dpm install

# Com configurações personalizadas
export DPM_MAX_RETRIES=15
export DPM_BASE_DELAY=5
dpm install
```

## Benefícios da Solução

1. **Robustez**: Lida automaticamente com rate limiting
2. **Configurável**: Permite personalização via variáveis de ambiente
3. **Inteligente**: Respeita as diretrizes do GitHub API
4. **Transparente**: Funciona sem mudanças no código do usuário
5. **Eficiente**: Minimiza o número de tentativas desnecessárias

## Monitoramento

### Logs de Rate Limiting

```
2025-08-07T11:46:17-0300 WARNING [dpm.install] Rate limit atingido. Aguardando 60.0 segundos...
2025-08-07T11:47:17-0300 INFO [dpm.install] Tentativa 2 falhou. Aguardando 2.1 segundos...
```

### Headers Monitorados

- `Retry-After`: Tempo sugerido para aguardar
- `X-RateLimit-Remaining`: Requisições restantes
- `X-RateLimit-Reset`: Timestamp do próximo reset

## Compatibilidade

A solução é totalmente compatível com:
- Configurações existentes
- Tokens de autenticação
- Repositórios públicos e privados
- Diferentes tipos de recursos

## Troubleshooting

### Se ainda ocorrerem erros 429:

1. **Aumente o delay base**: `export DPM_BASE_DELAY=5`
2. **Aumente o número de tentativas**: `export DPM_MAX_RETRIES=20`
3. **Verifique o token**: Certifique-se de que `GITHUB_PAT` está configurado
4. **Monitore os logs**: Use `export DPM_LOG_LEVEL=DEBUG` para mais detalhes

### Para uso em CI/CD:

```yaml
# .github/workflows/ci.yml
env:
  DPM_MAX_RETRIES: 20
  DPM_BASE_DELAY: 10
  DPM_MAX_DELAY: 300
```

## Contribuição

Esta solução foi desenvolvida para resolver o issue [#184](https://github.com/splor-mg/atividades/issues/184) e pode ser expandida para outros provedores de API que implementem rate limiting similar.
