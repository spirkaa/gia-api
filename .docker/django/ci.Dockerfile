ARG PYTHON_IMAGE=python:3.10-slim-bullseye
ARG BUILD_IMAGE=git.devmem.ru/cr/python:3.10-bullseye-venv-builder

FROM ${BUILD_IMAGE} AS builder

ARG BUILD_ENVIRONMENT=production
ARG APP_NAME=gia-api

COPY ${APP_NAME}/requirements .

RUN set -eux \
    && pip install --no-cache-dir -r ${BUILD_ENVIRONMENT}.txt


FROM ${PYTHON_IMAGE} AS runner

ARG S6_OVERLAY_RELEASE=v2.2.0.3

ADD https://github.com/just-containers/s6-overlay/releases/download/${S6_OVERLAY_RELEASE}/s6-overlay-amd64.tar.gz /tmp/s6overlay.tar.gz

RUN set -eux \
    && tar xzf /tmp/s6overlay.tar.gz -C / \
    && rm /tmp/s6overlay.tar.gz

ARG APP_NAME=gia-api
ARG APP_HOME=/app

ENV PYTHONUNBUFFERED=1

WORKDIR ${APP_HOME}

RUN set -eux \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        busybox-static \
        libpq-dev \
    && ln -s /bin/busybox /usr/sbin/crontab \
    && ln -s /bin/busybox /usr/sbin/crond \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && rm -rf /var/lib/apt/lists/*

COPY .docker/django/rootfs /

COPY --from=builder /opt/venv /opt/venv

COPY ${APP_NAME} ${APP_HOME}

ENV PATH="/opt/venv/bin:$PATH"

ENTRYPOINT [ "/init" ]
