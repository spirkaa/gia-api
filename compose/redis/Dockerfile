FROM redis:alpine

ENV TZ=Europe/Moscow

RUN set -eux \
    && ln -sf /usr/share/zoneinfo/${TZ} /etc/localtime

COPY redis.conf /usr/local/etc/redis/redis.conf

CMD ["redis-server", "/usr/local/etc/redis/redis.conf"]
