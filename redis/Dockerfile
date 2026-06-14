FROM redis:7-alpine@sha256:6ab0b6e7381779332f97b8ca76193e45b0756f38d4c0dcda72dbb3c32061ab99

RUN apk upgrade --no-cache

USER redis

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD redis-cli ping || exit 1

CMD ["redis-server", "--appendonly", "yes"]