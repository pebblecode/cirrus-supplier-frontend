SHELL := /bin/bash
VIRTUALENV_ROOT := $(shell [ -z $$VIRTUAL_ENV ] && echo $$(pwd)/venv || echo $$VIRTUAL_ENV)
rootdir =$(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
deploydir = $(rootdir)/build
to_deploy = app \
	    application.py \
	    config.py \
	    .coveragerc \
	    .ebextensions \
	    Procfile \
	    requirements.txt \
	    scripts \
	    setup.cfg \
	    spec \
	    tests
app_dir = $(rootdir)/app
assets = app/assets/cirrus-base \
	 app/assets/scss/toolkit \
	 app/content \
	 app/static \
	 app/templates/cirrus-base \
	 app/templates/toolkit

run_all: requirements frontend_build run_app

run_app: show_environment virtualenv
	python application.py runserver

virtualenv:
	[ -z $$VIRTUAL_ENV ] && [ ! -d venv ] && virtualenv venv || true

requirements: virtualenv requirements.txt
	${VIRTUALENV_ROOT}/bin/pip install -r requirements.txt

requirements_for_test: virtualenv requirements_for_test.txt
	${VIRTUALENV_ROOT}/bin/pip install -r requirements_for_test.txt

frontend_build:
	npm install --silent  && npm run frontend-install && npm run --silent frontend-build:production

test: show_environment test_pep8 test_python test_javascript

test_pep8: virtualenv
	${VIRTUALENV_ROOT}/bin/pep8 .

test_python: virtualenv
	${VIRTUALENV_ROOT}/bin/py.test ${PYTEST_ARGS}

test_javascript: frontend_build
	npm test

show_environment:
	@echo "Environment variables in use:"
	@env | grep DM_ || true

bundle_app:
	mkdir -p $(deploydir)
	for dir in $(to_deploy); do \
		cp -r $$dir $(deploydir); \
	done

bundle_assets:
	mkdir -p $(deploydir)
	for dir in $(assets); do \
		cp -r $$dir $(deploydir); \
	done

.PHONY: run_all run_app virtualenv requirements requirements_for_test frontend_build test test_pep8 test_python test_javascript show_environment bundle_app
