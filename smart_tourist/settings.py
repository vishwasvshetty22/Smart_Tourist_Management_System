"""
Smart Tourist - Django Settings (SQLite version)
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# SECRET_KEY / DEBUG can be overridden by environment variables on the server.
# Locally (no env vars set) it behaves exactly as before.
SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'django-insecure-smart-tourist-sqlite-key-change-in-production-2024'
)
DEBUG = os.environ.get('DJANGO_DEBUG', 'True') == 'True'

# Comma-separated list of allowed hosts, e.g. "yourusername.pythonanywhere.com"
_allowed = os.environ.get('DJANGO_ALLOWED_HOSTS', '')
ALLOWED_HOSTS = [h.strip() for h in _allowed.split(',') if h.strip()] or ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts',
    'vehicles',
    'hotels',
    'guides',
    'bookings',
    'payments',
    'ai_assistant',
    'notifications',
    'admin_dashboard',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'smart_tourist.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'smart_tourist.wsgi.application'

# ── SQLite Database ───────────────────────────────────────────────────────────
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ── Auth ──────────────────────────────────────────────────────────────────────
AUTH_USER_MODEL = 'accounts.User'
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ── Internationalisation ──────────────────────────────────────────────────────
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# ── Static & Media ────────────────────────────────────────────────────────────
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ── Session ───────────────────────────────────────────────────────────────────
SESSION_COOKIE_AGE = 86400
SESSION_SAVE_EVERY_REQUEST = True

# ── Email (optional – configure for real emails) ──────────────────────────────
# ── Email Configuration (Gmail SMTP) ─────────────────────────────────────────
# IMPORTANT: Replace EMAIL_HOST_PASSWORD with your Gmail App Password
# To get an App Password: Google Account → Security → 2-Step Verification → App passwords
EMAIL_BACKEND      = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST         = 'smtp.gmail.com'
EMAIL_PORT         = 587
EMAIL_USE_TLS      = True
EMAIL_HOST_USER    = 'vishwasshetty2580@gmail.com'
EMAIL_HOST_PASSWORD = 'YOUR_GMAIL_APP_PASSWORD'   # <-- Replace with your Gmail App Password
DEFAULT_FROM_EMAIL = 'SmartTourist <vishwasshetty2580@gmail.com>'

# ── Optional API Keys ─────────────────────────────────────────────────────────
# Paste your real keys here; platform works without them (fallback mode)
OPENAI_API_KEY    = ''          # https://platform.openai.com
WEATHER_API_KEY   = ''          # https://openweathermap.org/api
GOOGLE_MAPS_KEY   = ''          # https://console.cloud.google.com

# ── Messages ──────────────────────────────────────────────────────────────────
from django.contrib.messages import constants as messages
MESSAGE_TAGS = {
    messages.DEBUG:   'secondary',
    messages.INFO:    'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR:   'danger',
}
