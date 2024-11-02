SHELL := /bin/bash

install:
	pip install poetry==1.8.3 poeblix==0.10.0
	poetry config virtualenvs.create false
	poetry install

create_env_file:
	cat .env_template > .env

api:
	uvicorn src.api.app:app --reload --port 8000

token:
	python -m http.server 8012 & sleep 1 && open http://localhost:8012/dev/firebase_token.html

docker-build:
	docker build -t app .

docker-run:
	docker run --env-file .env -p 8000:8000 app
