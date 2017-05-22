FROM nginx:alpine
ADD nginx.conf /etc/nginx/nginx.conf

RUN apk add --no-cache tzdata

RUN ln -sf /usr/share/zoneinfo/Europe/Moscow /etc/localtime
