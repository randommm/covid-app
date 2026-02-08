FROM python:3.13

RUN pip install uv

COPY uv.lock /app/uv.lock
COPY pyproject.toml /app/pyproject.toml
RUN cd /app && ls && uv sync

COPY app /app

WORKDIR /app

RUN uv run python preprocessing.py

CMD uv run gunicorn index:server -b :8081 -t 900 \
    --workers 3 --error-logfile output.log \
    --access-logfile access.log --capture-output --log-level debug
