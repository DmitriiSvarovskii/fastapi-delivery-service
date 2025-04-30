import logging
from celery import Celery

from src.configs import celery_settings
from src.utils.logging import configure_logging


configure_logging()

logger = logging.getLogger(__name__)


celery_app = Celery(
    "delivery_tasks",
    broker=celery_settings.CELERY_BROKER_URL,
    backend=celery_settings.CELERY_RESULT_BACKEND,
    include=["src.tasks.package"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Europe/Moscow",
    enable_utc=False,
)

logger.info(
    "Celery app initialized: broker=%s, backend=%s",
    celery_settings.CELERY_BROKER_URL,
    celery_settings.CELERY_RESULT_BACKEND
)
