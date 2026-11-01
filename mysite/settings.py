# INF601 - Advanced Programming in Python
# Kyle Horn
# Mini Project 6

"""Django settings for the Master Catch site (the ``mysite`` project).

Secrets such as the SECRET_KEY are read from a ``.env`` file that sits
next to ``manage.py`` and is never committed to GitHub.

Settings reference: https://docs.djangoproject.com/en/6.1/ref/settings/
"""

# Standard library: read environment variables and build file paths.
import os
from pathlib import Path

# Django: message level names so we can rename one for Bootstrap below.
from django.contrib.messages import constants as message_constants
# Third party: loads the KEY=value lines from .env into the environment.
from dotenv import load_dotenv

# The project's top folder (the one holding manage.py). Every other path
# in this file is built from it so the site works on any computer.
BASE_DIR = Path(__file__).resolve().parent.parent

# Read .env so os.environ below can see DJANGO_SECRET_KEY and DJANGO_DEBUG.
load_dotenv(BASE_DIR / '.env')


# --- Security ---------------------------------------------------------------

# Used to sign login sessions and form tokens. It comes from .env, so it is
# never on GitHub. The site refuses to start if it is missing.
SECRET_KEY = os.environ['DJANGO_SECRET_KEY']

# Debug pages show code and settings when something breaks, so DEBUG is off
# unless .env says DJANGO_DEBUG=True (only on my own PC, never the dev box).
DEBUG = os.environ.get('DJANGO_DEBUG', 'False') == 'True'

# Web addresses this site will answer to: the dev box site, plus my PC.
ALLOWED_HOSTS = ['dev-student10.fhsucyber.com', 'localhost', '127.0.0.1']

# Forms submitted from this HTTPS address are trusted (fixes 403 CSRF errors).
CSRF_TRUSTED_ORIGINS = ['https://dev-student10.fhsucyber.com']


# --- Application definition -------------------------------------------------

# Every app Django loads: the built-in ones, then my Master_Catch app.
INSTALLED_APPS = [
    'django.contrib.admin',          # the /admin/ site
    'django.contrib.auth',           # users, passwords, login
    'django.contrib.contenttypes',   # lets admin and auth track models
    'django.contrib.sessions',       # remembers who is logged in
    'django.contrib.messages',       # one-time alerts like "Record saved"
    'django.contrib.staticfiles',    # CSS/JS files (used by the admin)
    'Master_Catch',                  # my fishing records app
]

# Code that runs on every request, in this order, before and after a view.
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',   # security headers
    'whitenoise.middleware.WhiteNoiseMiddleware',      # serves static files
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',       # blocks forged forms
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # request.user
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',  # no iframes
]

# The file that holds the site's main list of URLs.
ROOT_URLCONF = 'mysite.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Project-wide templates (base.html, login, register) live here.
        'DIRS': [BASE_DIR / 'templates'],
        # Also look in each app's own templates/ folder.
        'APP_DIRS': True,
        'OPTIONS': {
            # Values every template gets for free (request, user, messages).
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Entry point the web server uses to run the site.
WSGI_APPLICATION = 'mysite.wsgi.application'


# --- Database ---------------------------------------------------------------

# SQLite keeps the whole database in one file, db.sqlite3 (not on GitHub).
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# --- Passwords --------------------------------------------------------------

# Rules a new password must pass: not too like the username, at least
# 8 characters, not a common password, and not only numbers.
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.'
                'UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.'
                'MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.'
                'CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.'
                'NumericPasswordValidator',
    },
]


# --- Login / logout ---------------------------------------------------------

# Where @login_required sends visitors who are not logged in.
LOGIN_URL = 'login'
# Where users land after logging in, and after logging out.
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'home'

# Bootstrap calls its red alert "danger", Django calls it "error".
# This makes Django's error messages use Bootstrap's red style.
MESSAGE_TAGS = {message_constants.ERROR: 'danger'}

# On the live site (DEBUG off) login cookies are only sent over HTTPS.
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG


# --- Language and time ------------------------------------------------------

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/Chicago'   # Kansas (Central) time
USE_I18N = True                 # allow translations
USE_TZ = True                   # store times in UTC, show them in TIME_ZONE


# --- Static files (CSS, JavaScript, images) ---------------------------------

# Web address prefix for static files.
STATIC_URL = 'static/'
# `collectstatic` copies all static files here. WhiteNoise serves them so
# the admin keeps its styling even with DEBUG off.
STATIC_ROOT = BASE_DIR / 'staticfiles'


# --- Email ------------------------------------------------------------------

# The site sends no real email. Anything Django tries to send is printed
# in the terminal instead.
MAILERS = {
    'default': {
        'BACKEND': 'django.core.mail.backends.console.EmailBackend',
    },
}
