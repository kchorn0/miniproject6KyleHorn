#!/usr/bin/env python
# INF601 - Advanced Programming in Python
# Kyle Horn
# Mini Project 6

"""Django's command-line utility for administrative tasks.

Examples: ``python manage.py runserver``, ``python manage.py migrate``.
"""
# os: set an environment variable. sys: read the command typed.
import os
import sys


def main():
    """Run the manage.py command that was typed (runserver, migrate...)."""
    # Tell Django which settings file to use (mysite/settings.py).
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
    try:
        # Django's function that runs commands like runserver and migrate.
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        # Django isn't installed or the venv isn't active: explain why.
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    # sys.argv is the typed command, e.g. ['manage.py', 'runserver'].
    execute_from_command_line(sys.argv)


# Only run main() when this file is run directly (python manage.py ...).
if __name__ == '__main__':
    main()
