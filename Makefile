SHELL := /bin/bash

run:
	@python3 saskatoon/manage.py runserver

init:
	@python3 -m pip install .['test']
	@saskatoon/fixtures/init

migrate:
	@python3 saskatoon/manage.py migrate

migrations:
	@python3 saskatoon/manage.py makemigrations

translations:
	@cd saskatoon && django-admin makemessages --locale fr --domain django

permissions:
	@python3 saskatoon/manage.py check_permissions
	@python3 saskatoon/manage.py export_permissions

collectstatic:
	@python3 saskatoon/manage.py collectstatic

lint:
	@tox -e ruff_format
	@tox -e css-beautify

staticchecks:
	@tox -e ruff_check
	@tox -e mypy
	@tox -e pytype
	@tox -e djlint

unittests:
	@tox -e unittests

baselines:
	@tox -e baselines
