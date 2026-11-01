# INF601 - Advanced Programming in Python
# Kyle Horn
# Mini Project 6

"""ASGI config for the mysite project.

ASGI is the newer (async) version of WSGI. Django creates this file,
but this project runs with ``runserver``, which uses wsgi.py instead.

More info: https://docs.djangoproject.com/en/6.1/howto/deployment/asgi/
"""

# os: set an environment variable.
import os

# Builds the object an ASGI web server calls for each request.
from django.core.asgi import get_asgi_application

# Tell Django which settings file to use (mysite/settings.py).
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')

# The site itself, ready for an ASGI web server to run.
application = get_asgi_application()
