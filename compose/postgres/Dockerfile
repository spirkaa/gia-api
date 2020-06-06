FROM postgres:9-alpine

ENV TZ=Europe/Moscow

RUN set -eux \
    && apk add --no-cache --virtual .tz \
        alpine-conf \
        tzdata \
    && /sbin/setup-timezone -z $TZ \
    && apk del .tz

COPY scripts /usr/local/bin

RUN set -eux \
    && chmod +x /usr/local/bin/restore \
    && chmod +x /usr/local/bin/list-backups \
    && chmod +x /usr/local/bin/backup
