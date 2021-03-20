FROM jfloff/alpine-python:3.8
LABEL maintainer="Ilya Pavlov <piv@devmem.ru>"

ENV PYTHONUNBUFFERED=1
ARG CRYPTOGRAPHY_DONT_BUILD_RUST=1

COPY ./gia-api/requirements /app/requirements

RUN set -eux \
    && apk add --no-cache \
        libpq \
        libxslt-dev \
        libxml2-dev \
        libffi-dev

RUN set -eux \
    && apk add --no-cache --virtual .build-deps \
        postgresql-dev \
	&& pip install --no-cache-dir -U pip wheel \
    && pip install --no-cache-dir -U -r /app/requirements/production.txt \
    && apk del --no-cache .build-deps \
    && rm -rf /var/cache/apk/*

COPY ./gia-api /app
COPY ./compose/django/gunicorn.sh /gunicorn.sh
COPY ./compose/django/entrypoint.sh /entrypoint.sh

RUN set -eux \
    && addgroup django \
    && adduser -D -G django django \
    && chown -R django /app \
    && sed -i 's/\r//' /entrypoint.sh \
    && sed -i 's/\r//' /gunicorn.sh \
    && chmod +x /entrypoint.sh \
    && chown django /entrypoint.sh \
    && chmod +x /gunicorn.sh \
    && chown django /gunicorn.sh

WORKDIR /app

USER django

ENTRYPOINT ["/entrypoint.sh"]
CMD ["/gunicorn.sh"]
