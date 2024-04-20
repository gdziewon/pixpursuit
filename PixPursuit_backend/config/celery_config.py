"""
config/celery_config.py

Sets up Celery with a broker and result backend, defining the periodic tasks and their schedules.
It configures the Celery application for asynchronous task execution in the project.
"""

from celery import Celery
from celery.schedules import crontab
from utils.constants import (CELERY_BROKER_URL, CELERY_RESULT_BACKEND,
                             UPDATE_AUTO_TAGS_SCHEDULE, CLUSTER_FACES_SCHEDULE, BEAT_SCHEDULE_FILE_PATH,
                             PREDICT_ALL_TAGS_TASK, GROUP_FACES_TASK)


def make_celery(app_name=__name__) -> Celery:
    """
    Initialize and configure the Celery app.

    Sets up the Celery app with a broker and result backend, and configures the periodic task schedule.

    :param app_name: Name of the Celery application, default is __name__.
    :return: Configured Celery application instance.
    """

    # Initialize Celery app with redis broker and backend
    celery_app = Celery(app_name,
                        broker=CELERY_BROKER_URL,
                        backend=CELERY_RESULT_BACKEND)

    # Schedule for periodic tasks
    celery_app.conf.beat_schedule = {
        'update-auto-tags-every-6-hours': {
            'task': PREDICT_ALL_TAGS_TASK,
            'schedule': crontab(minute='0', hour=UPDATE_AUTO_TAGS_SCHEDULE),
        },
        'cluster-faces-every-3-hours': {
            'task': GROUP_FACES_TASK,
            'schedule': crontab(minute='0', hour=CLUSTER_FACES_SCHEDULE),
        },
    }

    # Save the schedule to a file
    celery_app.conf.beat_schedule_filename = BEAT_SCHEDULE_FILE_PATH

    # Other Celery configurations
    celery_app.conf.timezone = 'CET'
    celery_app.conf.task_default_queue = 'default'
    celery_app.conf.task_routes = {
        '*.main': {'queue': 'main_queue'},
        '*.beat': {'queue': 'beat_queue'}
    }

    return celery_app


celery = make_celery()
