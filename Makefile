SHELL := /bin/bash
DISPLAY := :0.0
DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
.PHONY: test lint build install-docs-dependencies build-docker

test:
	pytest tests/

coverage:
	coverage run --source=src -m pytest -v tests && coverage report -m

lint:
	pycodestyle src/
	pydocstyle src/

build:
	pyinstaller -F -w -n logsim --add-data "src/logicgate.png:." src/logsim.py

install-docs-dependencies:
	pip install -r requirements_docs.txt

docs: install-docs-dependencies
	cd docs && make html

build-docker:
	docker build -t logsim:latest .

run-docker: build-docker
	docker run --rm -e DISPLAY=$(DISPLAY) -e FILE=$(FILE) logsim
