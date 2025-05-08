FROM postgres:17-alpine

COPY scripts /usr/local/bin

RUN set -eux \
    && chmod +x /usr/local/bin/restore \
    && chmod +x /usr/local/bin/list-backups \
    && chmod +x /usr/local/bin/backup \
    && sed -i 's/\r//' /usr/local/bin/restore \
    && sed -i 's/\r//' /usr/local/bin/list-backups \
    && sed -i 's/\r//' /usr/local/bin/backup
