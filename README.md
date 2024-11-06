# Data Package Manager (dpm)

[![Tests](https://github.com/splor-mg/dpm/actions/workflows/tests.yaml/badge.svg)](https://github.com/splor-mg/dpm/actions/)
[![Coverage](https://codecov.io/gh/splor-mg/dpm/branch/main/graph/badge.svg)](https://app.codecov.io/gh/splor-mg/dpm)

## Docker

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

## Testes

Para rodar os testes execute:

```bash
python -m pytest
```
