# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Overview

Django REST API for the Learning Platform. Uses pipenv, PostgreSQL, and GitHub OAuth (dj-rest-auth + django-allauth). This repo is one of three siblings under the learning-platform workspace:
- learn-ops-api (this repo)
- learn-ops-client (React client)
- learn-ops-infrastructure (Docker Compose dev environment)

## Common Commands

Run these from the repo root unless noted.

### Environment setup
- Copy env template and set values:
  - cp .env.template .env
- Python and dependencies:
  - pipenv --python 3.11.11
  - pipenv install
  - pipenv shell

### Run server (local)
- pipenv run python manage.py migrate
- pipenv run python manage.py runserver 0.0.0.0:8000

### Run via Docker (containerized dev)
- From sibling infra repo: docker-compose up -d
- Django commands in container, e.g.:
  - docker-compose exec api pipenv run python manage.py migrate
  - docker-compose exec api pipenv run python manage.py shell

### Tests
- All tests: pipenv run python manage.py test
- Single app: pipenv run python manage.py test LearningAPI
- Single test case: pipenv run python manage.py test LearningAPI.tests:SomeTestCase
- Single test method: pipenv run python manage.py test LearningAPI.tests:SomeTestCase.test_method

### Lint and format
- Lint: pipenv run pylint LearningAPI LearningPlatform manage.py
- Format: pipenv run autopep8 --in-place --recursive LearningAPI LearningPlatform

### Database and admin
- DB shell: pipenv run python manage.py dbshell
- Create superuser: pipenv run python manage.py createsuperuser
- Collect static: pipenv run python manage.py collectstatic --noinput

## Architecture

- Project layout follows standard DRF patterns:
  - LearningAPI/models: domain modules grouped by subpackages (coursework, people, skill) plus tag.py
  - LearningAPI/serializers: DRF serializers per resource
  - LearningAPI/views: API endpoints per domain
  - LearningAPI/fixtures: development data loaded on startup in container workflows
- Settings module: LearningPlatform.settings
- Authentication: GitHub OAuth via dj-rest-auth/django-allauth. OAuth callback is handled by the API then redirects back to the client.

### Container entrypoint behavior (when using Docker)
- Waits for Postgres to be ready
- Applies migrations
- Creates fixtures on first run (socialaccount for GitHub app; superuser)
- Loads complete_backup fixture if present
- Collects static
- Starts runserver (port 8000)

## Environment

- Required variables (see .env.template):
  - LEARN_OPS_CLIENT_ID, LEARN_OPS_SECRET_KEY (GitHub OAuth)
  - LEARN_OPS_DJANGO_SECRET_KEY
  - LEARN_OPS_DB, LEARN_OPS_USER, LEARN_OPS_PASSWORD, LEARN_OPS_HOST, LEARN_OPS_PORT
  - LEARN_OPS_SUPERUSER_NAME, LEARN_OPS_SUPERUSER_PASSWORD
  - LEARNING_GITHUB_CALLBACK (used by client redirect)
- Allowed hosts default includes api.learning.local, 127.0.0.1, localhost

## Integration notes

- Client expects API at REACT_APP_API_URI (default http://localhost:8000 in client .env.development)
- For containerized dev, run services from learn-ops-infrastructure; for local dev, ensure Postgres matches your .env

