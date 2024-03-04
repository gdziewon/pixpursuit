from celery import Celery
from celery.schedules import crontab
from utils.constants import (CELERY_BROKER_URL, CELERY_RESULT_BACKEND,
                             UPDATE_AUTO_TAGS_SCHEDULE, CLUSTER_FACES_SCHEDULE, BEAT_SCHEDULE_FILE_PATH)


def make_celery(app_name=__name__) -> Celery:
    celery_app = Celery(app_name,
                        broker=CELERY_BROKER_URL,
                        backend=CELERY_RESULT_BACKEND)
    celery_app.conf.beat_schedule = {
        'update-auto-tags-every-15-min': {
            'task': 'tag_prediction_tools.update_all_auto_tags.beat',
            'schedule': crontab(minute=UPDATE_AUTO_TAGS_SCHEDULE)
        },
        'cluster-faces-every-5-min': {
            'task': 'face_operations.group_faces.beat',
            'schedule': crontab(minute=CLUSTER_FACES_SCHEDULE),
        },
    }
    celery_app.conf.timezone = 'CET'
    celery_app.conf.task_default_queue = 'default'
    celery_app.conf.task_routes = {
        '*.main': {'queue': 'main_queue'},
        '*.beat': {'queue': 'beat_queue'}
    }
    celery_app.conf.beat_schedule_filename = BEAT_SCHEDULE_FILE_PATH

    return celery_app


celery = make_celery()

# test_04.03
