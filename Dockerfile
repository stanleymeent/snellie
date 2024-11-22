FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN pip install poetry

RUN poetry config virtualenvs.create false && poetry install --no-dev

COPY . .

ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["uvicorn", "src.api.app:app", "--host", "0.0.0.0", "--port", "8013", "--reload"]