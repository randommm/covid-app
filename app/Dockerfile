FROM python

RUN pip install poetry

COPY poetry.lock /app/app/poetry.lock
COPY pyproject.toml /app/app/pyproject.toml
RUN cd /app/app && ls && poetry install

COPY . /app/app

