SHELL := /bin/bash
DISPLAY := :0.0
DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
.PHONY: install test lint build

test:
	pytest tests/

lint:
	pycodestyle src/
	pydocstyle src/

build:
	docker build -t logsim:latest .

run: build
	docker run --rm -e DISPLAY=$(DISPLAY) -e FILE=$(FILE) logsim
