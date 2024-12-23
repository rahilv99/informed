from celery import Celery

# Configure Celery app
celery_app = Celery(
    "tasks",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0",
    include=["tasks"]  # Specify the tasks module
)

celery_app.conf.update(
    timezone="UTC",
    enable_utc=True,
    beat_schedule={},  # Empty; will be set dynamically in beat_schedule.py
)
