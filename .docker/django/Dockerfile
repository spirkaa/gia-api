# hadolint global ignore=DL3006,DL3008,DL3013

ARG RUNTIME_IMAGE=python:3.11-slim-bookworm

FROM ${RUNTIME_IMAGE} AS python

FROM python AS build

ARG BUILD_ENVIRONMENT=production
ARG APP_NAME=gia-api

SHELL [ "/bin/bash", "-euxo", "pipefail", "-c" ]

RUN apt-get update \
    && apt-get install -y --no-install-suggests --no-install-recommends \
        build-essential \
        libpq-dev

RUN python -m venv /opt/venv \
    && pip install --no-cache-dir --upgrade pip wheel

ENV PATH="/opt/venv/bin:$PATH"

COPY ${APP_NAME}/requirements /

RUN pip install --no-cache-dir -r ${BUILD_ENVIRONMENT}.txt


FROM python AS runtime

ARG APP_NAME=gia-api
ARG APP_HOME=/app

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

SHELL [ "/bin/bash", "-euxo", "pipefail", "-c" ]

RUN addgroup --system --gid 1000 django \
    && adduser --system --uid 1000 --ingroup django django

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends \
        libpq-dev \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && rm -rf /var/lib/apt/lists/*

COPY --from=build /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY --chown=django:django .docker/django/scripts/entrypoint-local /entrypoint
COPY --chown=django:django .docker/django/scripts/start /start

RUN sed -i 's/\r$//g' /entrypoint \
    && chmod +x /entrypoint \
    && sed -i 's/\r$//g' /start \
    && chmod +x /start

COPY --chown=django:django ${APP_NAME} ${APP_HOME}

WORKDIR ${APP_HOME}

USER django

ENTRYPOINT [ "/entrypoint" ]
