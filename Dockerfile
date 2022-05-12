FROM python:3
LABEL version="0.1"
LABEL description="Docker image for logic simulator"

COPY ./requirements.txt /logsim/requirements.txt

WORKDIR /logsim

RUN pip install --no-cache-dir -r requirements.txt

