from celery import Celery
from celery.schedules import crontab


def make_celery(app_name=__name__):
    celery_app = Celery(app_name,
                        broker='redis://localhost:6379/0',
                        backend='redis://localhost:6379/0')
    celery_app.conf.beat_schedule = {
        'update-auto-tags-daily': {
            'task': 'tag_prediction_tools.update_all_auto_tags',
            'schedule': crontab(hour='1')
        },
    }
    celery_app.conf.timezone = 'CET'
    celery_app.conf.task_default_queue = 'default'
    celery_app.conf.task_routes = {
        'tag_prediction_tools.*': {'queue': 'tag_prediction_tools'},
    }

    return celery_app


celery = make_celery()
import tag_prediction_tools
import app
