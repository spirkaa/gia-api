FROM postgres:12-alpine

COPY scripts /usr/local/bin

RUN set -eux \
    && chmod +x /usr/local/bin/restore \
    && chmod +x /usr/local/bin/list-backups \
    && chmod +x /usr/local/bin/backup
