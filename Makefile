.PHONY: install run migrate superuser test coverage lint format check docs docs-build up down logs docker-test

PYTHON ?= python
MANAGE = $(PYTHON) manage.py
TEST_SETTINGS = --settings=config.settings.test

install:
	$(PYTHON) -m pip install -r requirements-dev.txt

run:
	$(MANAGE) runserver

migrate:
	$(MANAGE) migrate

superuser:
	$(MANAGE) createsuperuser

test:
	$(MANAGE) test $(TEST_SETTINGS)

coverage:
	coverage run manage.py test $(TEST_SETTINGS)
	coverage report

lint:
	ruff check .
	ruff format --check .

format:
	ruff check . --fix
	ruff format .

check:
	$(MANAGE) check
	$(MANAGE) makemigrations --check --dry-run

docs:
	mkdocs serve

docs-build:
	mkdocs build --strict

up:
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f web

docker-test:
	docker compose run --rm -e DJANGO_SETTINGS_MODULE=config.settings.test -e DJANGO_RUN_MIGRATIONS=0 web python manage.py test
