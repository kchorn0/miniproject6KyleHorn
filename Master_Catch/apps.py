# INF601 - Advanced Programming in Python
# Kyle Horn
# Mini Project 6

"""App configuration for Master_Catch (created by ``startapp``)."""

# Base class Django uses to describe an app.
from django.apps import AppConfig


class MasterCatchConfig(AppConfig):
    """Settings for the Master_Catch app.

    Django finds this class automatically because 'Master_Catch' is in
    INSTALLED_APPS in settings.py.
    """

    # The app's Python package (folder) name.
    name = 'Master_Catch'
