ARG PYTHON_IMAGE=python:3.10.4-slim-bullseye

FROM ${PYTHON_IMAGE} AS python

FROM python AS builder

ARG BUILD_ENVIRONMENT=production
ARG APP_NAME=gia-api

RUN set -eux \
    && apt-get update \
    && apt-get install -y --no-install-suggests --no-install-recommends \
        build-essential \
        libpq-dev

RUN set -eux \
    && python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY ${APP_NAME}/requirements .

RUN set -eux \
    && pip install --no-cache-dir -r ${BUILD_ENVIRONMENT}.txt


FROM python AS runner

ARG APP_NAME=gia-api
ARG APP_HOME=/app

ENV PYTHONUNBUFFERED=1

WORKDIR ${APP_HOME}

RUN set -eux \
    && apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y --no-install-suggests --no-install-recommends \
        libpq-dev \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /opt/venv /opt/venv

RUN set -eux \
    && addgroup --system --gid 1000 django \
    && adduser --system --uid 1000 --ingroup django django

COPY --chown=django:django .docker/django/scripts /

RUN set -eux \
    && sed -i 's/\r$//g' /entrypoint \
    && chmod +x /entrypoint \
    && sed -i 's/\r$//g' /start \
    && chmod +x /start

COPY --chown=django:django ${APP_NAME} ${APP_HOME}

RUN set -eux \
    && chown django:django ${APP_HOME}

USER django

ENV PATH="/opt/venv/bin:$PATH"

ENTRYPOINT [ "/entrypoint" ]
