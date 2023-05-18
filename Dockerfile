FROM python:3

WORKDIR /project

COPY requirements.txt ./
COPY requirements-docker.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r requirements-docker.txt

ENTRYPOINT ["/bin/bash"]
