FROM docker.io/nginx:1.27.3-alpine

COPY ./compose/production/nginx/nginx.conf /etc/nginx/nginx.conf
COPY ./compose/production/nginx/conf.d/default.conf /etc/nginx/conf.d/default.conf

COPY ./certs /etc/nginx/certs
