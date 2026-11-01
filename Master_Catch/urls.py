# INF601 - Advanced Programming in Python
# Kyle Horn
# Mini Project 6

"""URL list for the Master_Catch app.

Each ``path()`` connects a web address to the view that builds the page.
The ``name`` lets templates link to a page with ``{% url 'name' %}``.
"""

# Django's ready-made login and logout views.
from django.contrib.auth import views as auth_views
from django.urls import path

from . import views
from .forms import LoginForm

urlpatterns = [
    # Public pages.
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    # My records (must be logged in).
    path("records/", views.dashboard, name="dashboard"),
    path("records/new/", views.add_catch, name="add_catch"),
    # <int:pk> grabs the record number from the address, e.g. /records/5/.
    path("records/<int:pk>/", views.catch_detail, name="catch_detail"),
    path(
        "records/<int:pk>/delete/",
        views.delete_catch,
        name="delete_catch",
    ),
    # Accounts.
    path("register/", views.register, name="register"),
    # Django's login view using my Bootstrap-styled form. Logged-in users
    # who open /login/ are sent straight to their records.
    path(
        "login/",
        auth_views.LoginView.as_view(
            authentication_form=LoginForm,
            redirect_authenticated_user=True,
        ),
        name="login",
    ),
    # Logs the user out (Django only allows this with a POST form).
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]
