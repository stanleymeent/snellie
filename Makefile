SHELL := /bin/bash
install:
	pip install poetry==1.8.3 poeblix==0.10.0
	poetry config virtualenvs.create false
	poetry install

create_env_file:
	cat .env_template > .env

api:
	uvicorn src.api.app:app --reload --port 8001
