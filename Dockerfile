FROM python:3.10.4-alpine as builder

RUN apk add --no-cache gcc musl-dev libffi-dev && \
    pip install poetry==1.5.1

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN --mount=type=cache,target=$POETRY_CACHE_DIR poetry install --without dev --no-root

FROM python:3.10.4-alpine as runtime

LABEL maintainer="Vincent Thirouin <vincent.thirouin@epita.fr>"

WORKDIR /app

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

COPY py_race_cond ./py_race_cond

EXPOSE 8080

CMD [ "python", "-m", "py_race_cond" ]
