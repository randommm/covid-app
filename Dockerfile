FROM python:3.11

RUN pip install poetry

COPY poetry.lock /app/poetry.lock
COPY pyproject.toml /app/pyproject.toml
RUN cd /app && ls && poetry install

COPY app /app

WORKDIR /app

RUN poetry run python preprocessing.py

CMD poetry run gunicorn index:server -b :8081 -t 900 \
    --workers 3 --error-logfile output.log \
    --access-logfile access.log --capture-output --log-level debug
