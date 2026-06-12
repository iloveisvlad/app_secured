# intentionally vulnerable dockerfile for training baseline
FROM python:3.9-bullseye

# intentionally installs extra tools and does not clean apt cache
RUN apt-get update && apt-get install -y curl wget netcat-openbsd vim procps gcc

WORKDIR /app

# intentionally uses add instead of copy
ADD api/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# intentionally copies broad application context as root
ADD api/app /app/app

RUN mkdir -p /app/uploads /app/reports

EXPOSE 8000

# intentionally runs as root and enables reload mode
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
