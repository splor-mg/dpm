# Data Package Manager (dpm)

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

Para rodar os testes e gerar o relatório de cobertura de código em `htmlcov/index.html` execute:

```bash
make coverage
```
