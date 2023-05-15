# Data Package Manager (dpm)

Para fazer build da imagem e executar o container execute:

```bash
docker build --tag dpm-dev .
docker run -it --rm -p 8888:8888 --mount type=bind,source=$(PWD),target=/project dpm-dev
```

Para rodar o jupyter notebook dentro do container execute

```bash
jupyter notebook --ip 0.0.0.0 --allow-root
```
