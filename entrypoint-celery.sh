#!/usr/bin/env sh
set -e

echo ">>> Ждём зависимости (MySQL, Redis, RabbitMQ)"
wait-for-it.sh db:3306 --strict --timeout=60
wait-for-it.sh rabbitmq:5672 --strict --timeout=60
wait-for-it.sh redis:6379 --strict --timeout=60

echo ">>> Запуск Celery worker"
exec celery -A src.celery_app worker --loglevel=info
echo ">>> Приложение запущено!"