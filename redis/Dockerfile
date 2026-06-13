FROM redis:7-alpine

RUN apk upgrade --no-cache

USER redis

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD redis-cli ping || exit 1

CMD ["redis-server", "--appendonly", "yes"]