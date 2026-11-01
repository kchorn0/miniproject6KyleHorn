# INF601 - Advanced Programming in Python
# Kyle Horn
# Mini Project 6

"""URL configuration for mysite project."""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("Master_Catch.urls")),
]
