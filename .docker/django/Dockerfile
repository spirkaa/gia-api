FROM python:3.9
LABEL maintainer="Ilya Pavlov <piv@devmem.ru>"

ENV PYTHONUNBUFFERED=1
ARG CRYPTOGRAPHY_DONT_BUILD_RUST=1

COPY gia-api/requirements /app/requirements

RUN set -eux \
    && pip install --no-cache-dir -U -r /app/requirements/production.txt

COPY gia-api /app
COPY .docker/django/gunicorn.sh /gunicorn.sh
COPY .docker/django/entrypoint.sh /entrypoint.sh

RUN set -eux \
    && useradd -ms /bin/bash django \
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
