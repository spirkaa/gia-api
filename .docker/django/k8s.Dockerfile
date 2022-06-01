ARG PYTHON_IMAGE=python:3.10-slim-bullseye
ARG BUILD_IMAGE=git.devmem.ru/projects/python:3.10-bullseye-venv-builder

FROM ${BUILD_IMAGE} AS builder

ARG BUILD_ENVIRONMENT=production
ARG APP_NAME=gia-api

COPY ${APP_NAME}/requirements .

RUN set -eux \
    && pip install --no-cache-dir -r ${BUILD_ENVIRONMENT}.txt


FROM ${PYTHON_IMAGE} AS runner

ARG APP_NAME=gia-api
ARG APP_HOME=/app

ENV PYTHONUNBUFFERED=1

WORKDIR ${APP_HOME}

RUN set -eux \
    && apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends \
        libpq-dev \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && rm -rf /var/lib/apt/lists/*

RUN set -eux \
    && addgroup --system --gid 1000 django \
    && adduser --system --uid 1000 --ingroup django django

COPY --from=builder --chown=django:django /opt/venv /opt/venv

COPY --chown=django:django .docker/django/scripts/entrypoint /

RUN set -eux \
    && sed -i 's/\r$//g' /entrypoint \
    && chmod +x /entrypoint

COPY --chown=django:django ${APP_NAME} ${APP_HOME}

RUN set -eux \
    && chown django:django ${APP_HOME}

USER django

ENV PATH="/opt/venv/bin:$PATH"

RUN DJANGO_SETTINGS_MODULE=config.settings.production \
    DJANGO_CACHE_URL=redis://redis:6379/1 \
    DJANGO_DATABASE_URL=sqlite:/// \
    DJANGO_DATABASE_ENGINE=django.db.backends.sqlite3 \
    DJANGO_SECRET_KEY=collectstatic \
    DJANGO_ALLOWED_HOSTS=* \
    python /app/manage.py collectstatic --noinput

EXPOSE 5000

ENTRYPOINT [ "/entrypoint" ]

CMD [ "gunicorn", "config.wsgi", "-b", "0.0.0.0:5000", "-w", "4", "-t", "60", "--chdir", "/app" ]
