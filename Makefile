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

collectstatic:
	@python3 saskatoon/manage.py collectstatic

staticcheck:
	@tox -e mypy
	@tox -e flake8
	@tox -e pytype

unittests:
	@tox -e unittests
