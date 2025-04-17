from .settings import *
import os

# Use SQLite for testing
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Disable password hashing for faster tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Disable email sending during tests
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Disable APPEND_SLASH for testing
APPEND_SLASH = False

# Configure middleware for testing
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

# Disable SSL redirect for testing
SECURE_SSL_REDIRECT = False

# Disable session cookie secure flag for testing
SESSION_COOKIE_SECURE = False

# Disable CSRF cookie secure flag for testing
CSRF_COOKIE_SECURE = False 