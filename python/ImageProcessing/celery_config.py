from celery import Celery


def make_celery(app_name=__name__):
    return Celery(app_name,
                  broker='redis://localhost:6379/0',
                  backend='redis://localhost:6379/0')


celery = make_celery()
import database_tools
import tag_prediction_tools
celery.autodiscover_tasks(['database_tools', 'tag_prediction_tools'])
