FROM jfloff/alpine-python:3.7

ENV PYTHONUNBUFFERED 1

# Requirements have to be pulled and installed here, otherwise caching won't work
COPY ./requirements /requirements

RUN echo "http://nl.alpinelinux.org/alpine/edge/main" > /etc/apk/repositories \
     && apk add --no-cache \
        tzdata \
        libpq \
        libxslt-dev \
        libxml2-dev \
        libffi-dev \
     && ln -sf /usr/share/zoneinfo/Europe/Moscow /etc/localtime \
     && apk add --no-cache --virtual .build-deps \
        postgresql-dev \
	&& pip install --upgrade pip \
    && pip install --no-cache-dir -U -r /requirements/production.txt \
    && apk del .build-deps

COPY . /app
COPY ./compose/django/gunicorn.sh /gunicorn.sh
COPY ./compose/django/entrypoint.sh /entrypoint.sh

RUN addgroup django \
    && adduser -D -G django django \
    && chown -R django /app \
    && sed -i 's/\r//' /entrypoint.sh \
    && sed -i 's/\r//' /gunicorn.sh \
    && chmod +x /entrypoint.sh \
    && chown django /entrypoint.sh \
    && chmod +x /gunicorn.sh \
    && chown django /gunicorn.sh

WORKDIR /app

ENTRYPOINT ["/entrypoint.sh"]
