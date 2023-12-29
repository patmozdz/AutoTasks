# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from .celery import app as celery_app

# Used to specify what gets import if 'from module import *' is used
__all__ = ('celery_app',)
