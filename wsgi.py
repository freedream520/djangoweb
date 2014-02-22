import os
from django.core.handlers.wsgi import WSGIHandler

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djangoweb.settings")
application = WSGIHandler()
