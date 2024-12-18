FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y git

RUN git clone https://github.com/stanleymeent/snellie.git .

COPY pyproject.toml poetry.lock ./

RUN pip install poetry

RUN poetry config virtualenvs.create false && poetry install --no-dev

COPY src/ src/

ENV PYTHONPATH=/app/src

EXPOSE 8013

CMD ["uvicorn", "src.api.app:app", "--host", "0.0.0.0", "--port", "8013", "--reload"]