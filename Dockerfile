FROM python:3.8.18

RUN pip install poetry

WORKDIR /app

COPY . /app

EXPOSE 8000

RUN poetry config virtualenvs.create false
RUN poetry install --no-dev

