from celery import Celery
from app import app
celery = Celery(
    'placement_portal',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0'
)

# Tell celery where tasks are
celery.conf.update(
    imports=['Controllers.tasks']
)