# hadolint global ignore=DL3006,DL3008,DL3013

ARG BUILD_IMAGE=ghcr.io/astral-sh/uv:python3.13-bookworm
ARG RUNTIME_IMAGE=ghcr.io/astral-sh/uv:python3.13-bookworm-slim

FROM ${BUILD_IMAGE} AS build

ENV UV_PYTHON_DOWNLOADS=never
ENV UV_PROJECT_ENVIRONMENT=/opt/venv

SHELL [ "/bin/bash", "-euxo", "pipefail", "-c" ]

# https://github.com/wilsonzlin/minify-html/issues/225
RUN apt-get update \
    && apt-get install -y --no-install-suggests --no-install-recommends \
        curl \
    && curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y

ARG UV_ARGS=""

COPY pyproject.toml uv.lock /

# https://github.com/wilsonzlin/minify-html/issues/225
# hadolint ignore=SC1091
RUN . "/root/.cargo/env" \
    && uv sync --locked ${UV_ARGS}


FROM ${RUNTIME_IMAGE} AS runtime

ARG APP_NAME=gia-api
ARG APP_HOME=/app

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV UV_PROJECT_ENVIRONMENT=/opt/venv

SHELL [ "/bin/bash", "-euxo", "pipefail", "-c" ]

RUN addgroup --system --gid 1000 django \
    && adduser --system --uid 1000 --ingroup django django

COPY --from=build ${UV_PROJECT_ENVIRONMENT} ${UV_PROJECT_ENVIRONMENT}
ENV PATH="${UV_PROJECT_ENVIRONMENT}/bin:${PATH}"

COPY --chown=django:django .docker/django/entrypoint /

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

CMD [ "gunicorn", "config.wsgi", "-c", "config/gunicorn.py", "-b", "0.0.0.0:5000", "-w", "4", "-t", "60", "--chdir", "/app" ]
