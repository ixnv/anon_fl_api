import os

from celery import Celery
from django.conf import settings


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "anon_fl.settings")

# settings.configure()
app = Celery('api')

CELERY_TIMEZONE = 'UTC'

app.config_from_object('django.conf.settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
