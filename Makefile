SHELL := /bin/bash

init:
	@saskatoon/fixtures/init

run:
	@python3 saskatoon/manage.py runserver

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

staticchecks:
	@tox -e mypy
	@tox -e ruff
	@tox -e pytype

unittests:
	@tox -e unittests
