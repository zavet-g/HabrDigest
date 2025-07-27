from celery import Celery
from app.core.config import settings

# Создаем экземпляр Celery
celery_app = Celery(
    "habrdigest",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["celery_app.tasks"]
)

# Конфигурация Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Europe/Moscow",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 минут
    task_soft_time_limit=25 * 60,  # 25 минут
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Периодические задачи
celery_app.conf.beat_schedule = {
    "parse-habr-articles": {
        "task": "celery_app.tasks.parse_habr_articles",
        "schedule": settings.parsing_interval_hours * 3600,  # В секундах
    },
    "send-digests": {
        "task": "celery_app.tasks.send_digests_to_users",
        "schedule": 3600,  # Каждый час
    },
    "process-articles": {
        "task": "celery_app.tasks.process_unprocessed_articles",
        "schedule": 1800,  # Каждые 30 минут
    },
} 