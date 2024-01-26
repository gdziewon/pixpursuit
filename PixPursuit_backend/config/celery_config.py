from celery import Celery
from celery.schedules import crontab
import os


def make_celery(app_name=__name__):
    celery_app = Celery(app_name,
                        broker='redis://localhost:6379/0',
                        backend='redis://localhost:6379/0')
    celery_app.conf.beat_schedule = {
        'update-auto-tags-every-15-min': {
            'task': 'tag_prediction_tools.update_all_auto_tags',
            'schedule': crontab(minute='*/15')
        },
        'cluster-faces-every-5-min': {
            'task': 'face_operations.group_faces',
            'schedule': crontab(minute='*/5'),
        },
    }
    celery_app.conf.timezone = 'CET'
    celery_app.conf.task_default_queue = 'default'
    celery_app.conf.task_routes = {
        '*.*': {'queue': 'main_queue'},
    }
    script_dir = os.path.dirname(os.path.abspath(__file__))
    beat_file_path = os.path.join(script_dir, '..', 'generated', 'celerybeat-schedule')
    celery_app.conf.beat_schedule_filename = beat_file_path

    return celery_app


celery = make_celery()
