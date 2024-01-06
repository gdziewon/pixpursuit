from celery import Celery
from celery.schedules import crontab


def make_celery(app_name=__name__):
    celery_app = Celery(app_name,
                        broker='redis://localhost:6379/0',
                        backend='redis://localhost:6379/0')
    celery_app.conf.beat_schedule = {
        'update-auto-tags-daily': {
            'task': 'tag_prediction_tools.update_all_auto_tags',
            'schedule': crontab(hour='*/6')
        },
        'cluster-faces-daily': {
            'task': 'database_tools.group_faces',
            'schedule': crontab(hour='*'),
        },
    }
    celery_app.conf.timezone = 'CET'
    celery_app.conf.task_default_queue = 'default'
    celery_app.conf.task_routes = {
        '*.*': {'queue': 'main_queue'},
    }

    return celery_app


celery = make_celery()
import tag_prediction_tools
import app
import database_tools
import face_detection
import object_detection
import feature_extraction
