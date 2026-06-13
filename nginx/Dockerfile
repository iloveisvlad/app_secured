FROM nginx:stable-alpine

RUN apk upgrade --no-cache

COPY nginx/main.conf /etc/nginx/nginx.conf
COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf

USER nginx

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD nginx -t || exit 1

ENTRYPOINT ["nginx"]
CMD ["-g", "daemon off;"]