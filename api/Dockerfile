FROM python:3.12-slim-trixie

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN groupadd --system --gid 10001 taskops \
    && useradd --system --uid 10001 --gid taskops --home-dir /app --shell /usr/sbin/nologin taskops

COPY api/requirements.txt /app/requirements.txt

RUN pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r /app/requirements.txt

COPY api/app /app/app

RUN mkdir -p /app/uploads /app/reports \
    && chown -R taskops:taskops /app

USER taskops

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3).read()" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]