from celery_app import celery_app
from celery.schedules import crontab

# Set periodic tasks
celery_app.conf.beat_schedule = {
    "run-main-pipeline-daily": {
        "task": "tasks.main_pipeline",
        "schedule": crontab(hour=12, minute=0),  # Trigger daily at 12:00 PM
        'args': (),
    },
}
