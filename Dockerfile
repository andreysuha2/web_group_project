FROM python:3.11-alpine

ENV APP_HOME=/app \
    POETRY_VERSION=1.7.1

WORKDIR $APP_HOME

COPY . .

RUN pip install "poetry==$POETRY_VERSION"

RUN \
    apk add --no-cache postgresql-libs && \
    apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev && \
    poetry install --no-root && \
    apk --purge del .build-deps

RUN \
    cd ./app && \
    poetry run alembic upgrade head && \
    cd .. && \
    poetry run python -m ./app/cli.py seed

ENTRYPOINT [ "poetry", "run", "python", "-m", "app.main" ]