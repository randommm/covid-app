FROM python

RUN pip install poetry

COPY poetry.lock /app/poetry.lock
COPY pyproject.toml /app/pyproject.toml
RUN cd /app && ls && poetry install

COPY app /app

