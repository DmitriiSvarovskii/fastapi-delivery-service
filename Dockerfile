FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    gcc \
    build-essential \
    libffi-dev \
    bash \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY wait-for-it.sh /usr/local/bin/wait-for-it.sh
COPY entrypoint-celery.sh /usr/local/bin/entrypoint-celery.sh
RUN chmod +x /usr/local/bin/wait-for-it.sh /usr/local/bin/entrypoint-celery.sh

COPY . .

ENV PYTHONPATH=/app


CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]