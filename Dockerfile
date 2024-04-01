FROM python:3.11-alpine

ENV APP_HOME=/photoshopper \
    POETRY_VERSION=1.7.1 

ENV PYTHONPATH=${APP_HOME}:$PYTHONPATH

WORKDIR $APP_HOME

COPY . .

RUN pip install "poetry==$POETRY_VERSION"

RUN \
    apk add --no-cache postgresql-libs && \
    apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev && \
    poetry install --no-root && \
    apk --purge del .build-deps

CMD \
    sleep 10 && \
    cd ./app && \
    poetry run alembic upgrade head && \
    cd .. && \
    poetry run python ./app/main.py