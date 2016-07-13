FROM python:3.5-alpine

ENV PYTHONUNBUFFERED 1

# Requirements have to be pulled and installed here, otherwise caching won't work
COPY ./requirements /requirements

RUN apk add --no-cache libpq \
        libxslt-dev \
        libxml2-dev \
     && apk add --no-cache --virtual .build-deps \
        git \
		build-base \
		python3-dev \
        postgresql-dev \
    && pip install -r /requirements/production.txt \
    && addgroup django \
    && adduser -D -G django django \
    && apk del .build-deps

COPY . /app
RUN chown -R django /app

COPY ./compose/django/gunicorn.sh /gunicorn.sh
COPY ./compose/django/entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r//' /entrypoint.sh \
    && sed -i 's/\r//' /gunicorn.sh \
    && chmod +x /entrypoint.sh \
    && chown django /entrypoint.sh \
    && chmod +x /gunicorn.sh \
    && chown django /gunicorn.sh

WORKDIR /app

ENTRYPOINT ["/entrypoint.sh"]
