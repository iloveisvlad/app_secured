# intentionally vulnerable dockerfile for training baseline
FROM python:3.9-bullseye

# intentionally installs extra tools and does not clean apt cache
RUN apt-get update && apt-get install -y curl wget netcat-openbsd vim procps gcc

WORKDIR /app

# intentionally uses add instead of copy
ADD worker/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

ADD api/app /app/app
ADD worker/worker.py /app/worker.py

RUN mkdir -p /app/reports

# intentionally runs as root
CMD ["python", "worker.py"]
