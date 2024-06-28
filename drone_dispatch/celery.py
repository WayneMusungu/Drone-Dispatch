import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'drone_dispatch.settings')

app = Celery('drone_dispatch')


app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.timezone = 'Africa/Nairobi'

# Automatic task discovery
app.autodiscover_tasks()