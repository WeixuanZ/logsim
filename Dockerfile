FROM ubuntu:20.04
LABEL version="0.1"
LABEL description="Docker image for logic simulator"

RUN apt-get update && apt-get install --no-install-recommends -y python3.9 python3.9-dev python3-pip python3-opengl python3-wxgtk4.0 freeglut3-dev

WORKDIR /logsim

COPY ./src/ /logsim/src/

CMD ["python3", "src/logsim.py", "${FILE}"]
