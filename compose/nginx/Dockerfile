FROM nginx:alpine

ENV TZ=Europe/Moscow

RUN set -eux \
    && ln -sf /usr/share/zoneinfo/${TZ} /etc/localtime

COPY nginx.conf /etc/nginx/nginx.conf
