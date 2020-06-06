FROM redis:alpine

ENV TZ=Europe/Moscow

RUN set -eux \
    && apk add --no-cache --virtual .tz \
        alpine-conf \
        tzdata \
    && /sbin/setup-timezone -z $TZ \
    && apk del .tz

COPY redis.conf /usr/local/etc/redis/redis.conf

CMD ["redis-server", "/usr/local/etc/redis/redis.conf"]
