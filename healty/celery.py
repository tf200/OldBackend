from __future__ import absolute_import, unicode_literals
import os
from celery import Celery


os.environ.setdefault('django.conf:settings', 'healty.settings')

app = Celery('healty')


app.config_from_object('django.conf:settings', namespace='CELERY')


app.autodiscover_tasks()