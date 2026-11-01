# INF601 - Advanced Programming in Python
# Kyle Horn
# Mini Project 6

from django.contrib.auth import views as auth_views
from django.urls import path

from . import views
from .forms import LoginForm

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("records/", views.dashboard, name="dashboard"),
    path("records/new/", views.add_catch, name="add_catch"),
    path("records/<int:pk>/", views.catch_detail, name="catch_detail"),
    path("records/<int:pk>/delete/", views.delete_catch, name="delete_catch"),
    path("register/", views.register, name="register"),
    path(
        "login/",
        auth_views.LoginView.as_view(authentication_form=LoginForm, redirect_authenticated_user=True),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]
