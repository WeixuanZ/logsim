SHELL := /bin/bash
DISPLAY := :0.0
DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
.PHONY: install test lint install-docs-dependencies build

test:
	pytest tests/

lint:
	pycodestyle src/
	pydocstyle src/

install-docs-dependencies:
	pip install -r requirements_docs.txt

docs: install-docs-dependencies
	cd docs && make html

build:
	docker build -t logsim:latest .

run: build
	docker run --rm -e DISPLAY=$(DISPLAY) -e FILE=$(FILE) logsim
