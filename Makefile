SHELL := /bin/bash
DISPLAY := :0.0
DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

LANGS := zh_CN  # list of supported langugages
LOCALE_DIR := src/locale


.PHONY: test
test:
	pytest tests/

.PHONY: coverage
coverage:
	coverage run --source=src -m pytest -v tests && coverage report -m

.PHONY: lint
lint:
	pycodestyle src/*.py
	pydocstyle src/*.py

LANG_DATA := $(foreach lang,$(LANGS),--add-data "$(LOCALE_DIR)/$(lang)/LC_MESSAGES/*.mo:./locale/$(lang)/LC_MESSAGES" )
build: compile-translation
	pyinstaller -F -w -n logsim --add-data "src/logicgate.png:." $(LANG_DATA) src/logsim.py

.PHONY: gettext
gettext:
	$(foreach lang,$(LANGS),mkdir -p $(LOCALE_DIR)/$(lang)/LC_MESSAGES;)
	find src/ -iname "*.py" | xargs xgettext --from-code utf-8 -d logsim -o logsim.pot -p $(LOCALE_DIR);
	$(foreach lang,$(LANGS),cp -n $(LOCALE_DIR)/logsim.pot $(LOCALE_DIR)/$(lang)/LC_MESSAGES/logsim.po;)

.PHONY: compile-translation
compile-translation:
	$(foreach lang,$(LANGS),msgfmt -o $(LOCALE_DIR)/$(lang)/LC_MESSAGES/logsim.mo $(LOCALE_DIR)/$(lang)/LC_MESSAGES/logsim;)

.PHONY: install-docs-dependencies
install-docs-dependencies:
	pip install -r requirements_docs.txt

docs: install-docs-dependencies
	cd docs && make html


.PHONY: build-docker
build-docker:
	docker build -t logsim:latest .

run-docker: build-docker
	docker run --rm -e DISPLAY=$(DISPLAY) -e FILE=$(FILE) logsim
