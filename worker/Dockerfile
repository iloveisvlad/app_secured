FROM python:3.12-slim-trixie@sha256:d764629ce0ddd8c71fd371e9901efb324a95789d2315a47db7e4d27e78f1b0e9

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN groupadd --system --gid 10001 taskops \
    && useradd --system --uid 10001 --gid taskops --home-dir /app --shell /usr/sbin/nologin taskops

COPY worker/requirements.txt /app/requirements.txt

RUN pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r /app/requirements.txt

COPY api/app /app/app
COPY worker/worker.py /app/worker.py

RUN mkdir -p /app/reports \
    && chown -R taskops:taskops /app

USER taskops

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import pathlib; cmd=pathlib.Path('/proc/1/cmdline').read_bytes(); raise SystemExit(0 if b'worker.py' in cmd else 1)"

CMD ["python", "worker.py"]