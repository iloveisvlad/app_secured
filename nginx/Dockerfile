FROM nginx:stable-alpine

RUN apk upgrade --no-cache

COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD nginx -t || exit 1

CMD ["nginx", "-g", "daemon off;"]