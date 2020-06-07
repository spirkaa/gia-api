FROM postgres:9-alpine

ENV TZ=Europe/Moscow

RUN set -eux \
    && ln -sf /usr/share/zoneinfo/${TZ} /etc/localtime

COPY scripts /usr/local/bin

RUN set -eux \
    && chmod +x /usr/local/bin/restore \
    && chmod +x /usr/local/bin/list-backups \
    && chmod +x /usr/local/bin/backup
