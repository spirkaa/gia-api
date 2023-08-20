# hadolint global ignore=DL3006,DL3008,DL3013

ARG BUILD_IMAGE=ghcr.io/spirkaa/python:3.11-bookworm-venv-builder
ARG RUNTIME_IMAGE=python:3.11-slim-bookworm

FROM ${BUILD_IMAGE} AS build

ARG BUILD_ENVIRONMENT=production
ARG APP_NAME=gia-api

SHELL [ "/bin/bash", "-euxo", "pipefail", "-c" ]

COPY ${APP_NAME}/requirements /

RUN set -eux \
    && pip install --no-cache-dir -r ${BUILD_ENVIRONMENT}.txt


FROM ${RUNTIME_IMAGE} AS runtime

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

COPY --chown=django:django .docker/django/scripts/entrypoint /

RUN sed -i 's/\r$//g' /entrypoint \
    && chmod +x /entrypoint

COPY --chown=django:django ${APP_NAME} ${APP_HOME}

WORKDIR ${APP_HOME}

USER django

RUN DJANGO_SETTINGS_MODULE="config.settings.production" \
    DJANGO_CACHE_URL="redis://redis:6379/1" \
    DJANGO_DATABASE_URL="sqlite:///" \
    DJANGO_DATABASE_ENGINE="django.db.backends.sqlite3" \
    DJANGO_SECRET_KEY="collectstatic" \
    DJANGO_ALLOWED_HOSTS="*" \
    python manage.py collectstatic --noinput

EXPOSE 5000

ENTRYPOINT [ "/entrypoint" ]

CMD [ "gunicorn", "config.wsgi", "-b", "0.0.0.0:5000", "-w", "4", "-t", "60", "--chdir", "/app" ]
