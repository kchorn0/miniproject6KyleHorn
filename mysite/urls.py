# INF601 - Advanced Programming in Python
# Kyle Horn
# Mini Project 6

"""Main URL list for the whole site.

Sends ``/admin/`` to the Django admin and every other address to the
Master_Catch app's own URL list in ``Master_Catch/urls.py``.
"""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # The built-in admin site, e.g. https://.../admin/
    path("admin/", admin.site.urls),
    # Everything else (home, about, records, login...) is handled by my app.
    path("", include("Master_Catch.urls")),
]
