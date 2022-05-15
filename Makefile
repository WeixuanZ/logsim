SHELL := /bin/bash
DISPLAY := :0.0
DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
.PHONY: install test lint docs build

test:
	pytest tests/

lint:
	pycodestyle src/
	pydocstyle src/

docs:
	cd docs && make html

build:
	docker build -t logsim:latest .

run: build
	docker run --rm -e DISPLAY=$(DISPLAY) -e FILE=$(FILE) logsim
