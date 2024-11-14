FROM nginx:alpine

COPY ./compose/local/nginx/nginx.conf /etc/nginx/nginx.conf
COPY ./compose/local/nginx/conf.d/default.conf /etc/nginx/conf.d/default.conf

COPY ./certs /etc/nginx/certs
