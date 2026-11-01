# INF601 - Advanced Programming in Python
# Kyle Horn
# Mini Project 6

"""WSGI config for the mysite project.

WSGI is the standard way a Python web server talks to a web app.
``runserver`` uses the ``application`` below (see WSGI_APPLICATION in
settings.py).

More info: https://docs.djangoproject.com/en/6.1/howto/deployment/wsgi/
"""

# os: set an environment variable.
import os

# Builds the object a WSGI web server calls for each request.
from django.core.wsgi import get_wsgi_application

# Tell Django which settings file to use (mysite/settings.py).
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')

# The site itself, ready for the web server to run.
application = get_wsgi_application()
