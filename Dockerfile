FROM python:3.12-slim-bullseye as bot

WORKDIR /app
RUN pip install poetry
COPY poetry.lock /app
COPY pyproject.toml /app
COPY poetry.toml /app
RUN poetry install --no-root

WORKDIR /app
COPY . /app
RUN poetry install

CMD alembic upgrade head && python main.py