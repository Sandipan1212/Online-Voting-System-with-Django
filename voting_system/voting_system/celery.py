# celery.py
import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "voting_system.settings")  # Replace with your project name

celery_app = Celery("voting_system")  # Replace with your project name
celery_app.config_from_object("django.conf:settings", namespace="CELERY")
celery_app.autodiscover_tasks()
# celery.py
import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "voting_system.settings")  # Replace with your project name

celery_app = Celery("voting_system")  # Replace with your project name
celery_app.config_from_object("django.conf:settings", namespace="CELERY")
celery_app.autodiscover_tasks()
