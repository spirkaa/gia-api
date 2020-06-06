FROM nginx:alpine

ENV TZ=Europe/Moscow

RUN set -eux \
    && apk add --no-cache --virtual .tz \
        alpine-conf \
        tzdata \
    && /sbin/setup-timezone -z $TZ \
    && apk del .tz

COPY nginx.conf /etc/nginx/nginx.conf
