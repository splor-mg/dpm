# Data Package Manager (dpm)

[![Tests](https://github.com/splor-mg/dpm/actions/workflows/tests.yaml/badge.svg)](https://github.com/splor-mg/actions/)
[![Coverage](https://codecov.io/gh/splor-mg/dpm/branch/main/graph/badge.svg)](https://app.codecov.io/gh/splor-mg/dpm)

## 🚀 Novidade: Solução para Rate Limiting

**Problema resolvido**: O DPM agora inclui uma solução robusta para o erro HTTP 429 (Too Many Requests) que pode ocorrer ao acessar o GitHub API.

**Solução implementada**:
- ✅ **Retry automático** com backoff exponencial
- ✅ **Respeita headers** `Retry-After` do GitHub
- ✅ **Monitora rate limiting** em tempo real
- ✅ **Configurável** via variáveis de ambiente
- ✅ **Logging inteligente** para debugging

**Para mais detalhes**: Veja [docs/rate_limiting_solution.md](docs/rate_limiting_solution.md)

## 🐳 Docker

Para fazer build da imagem e executar o container execute:

```bash
docker build --tag dpm-dev .
docker run -it --rm -p 8888:8888 --mount type=bind,source=$(PWD),target=/project dpm-dev
```

Para rodar o jupyter notebook dentro do container execute

```bash
jupyter notebook --ip 0.0.0.0 --allow-root
```

Para executar o código usando Docker no Pycharm, utilizar [este guia](https://github.com/splor-mg/dpm/issues/5).

## 🧪 Testes

Para rodar os testes execute:

```bash
python -m pytest
```

## 📚 Documentação

- [Getting Started](docs/getting_started.md) - Guia de início rápido
- [Rate Limiting Solution](docs/rate_limiting_solution.md) - Solução para HTTP 429
- [Reference](docs/reference.md) - Referência da API

## ⚙️ Configuração de Rate Limiting

### Configurações Padrão

```bash
# Número máximo de tentativas
export DPM_MAX_RETRIES=5

# Delay base entre tentativas (em segundos)
export DPM_BASE_DELAY=1

# Delay máximo entre tentativas (em segundos)
export DPM_MAX_DELAY=60

# Fator de backoff exponencial
export DPM_BACKOFF_FACTOR=1

# Timeout para requisições (em segundos)
export DPM_TIMEOUT=30

# Nível de logging
export DPM_LOG_LEVEL=INFO
```

### Exemplo de Uso

```bash
# Configurar para ser mais agressivo com retries
export DPM_MAX_RETRIES=15
export DPM_BASE_DELAY=5
export DPM_MAX_DELAY=300

# Executar com as novas configurações
dpm install
```

## 🔧 Instalação

```bash
pip install dpm
```

## 📖 Uso Básico

1. **Crie um arquivo `data.toml`**:

```toml
[packages]
[packages.meu_pacote]
path = "https://raw.githubusercontent.com/org/repo/main/datapackage.json"
token = "GITHUB_PAT"  # Opcional, para repositórios privados
```

2. **Execute o comando**:

```bash
dpm install
```

## 🤝 Contribuição

Para contribuir com o projeto:

1. Faça um fork do repositório
2. Crie uma branch para sua feature
3. Implemente suas mudanças
4. Adicione testes
5. Faça commit e push
6. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.
