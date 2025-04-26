from .settings import *
import os

# Override database settings for testing
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'test_neondb',
        'USER': 'neondb_owner',
        'PASSWORD': 'npg_jA7FayGrgl4R',
        'HOST': 'ep-quiet-glitter-a48dfo8n-pooler.us-east-1.aws.neon.tech',
        'PORT': '5432',
        'OPTIONS': {
            'sslmode': 'require',
            'connect_timeout': 5,
        },
        'TEST': {
            'NAME': 'test_test_neondb',
            'CONN_MAX_AGE': 0,  # Force new connection for each test
        }
    }
}

# Disable password hashing for faster tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Disable email sending during tests
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

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

# Template settings for testing
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
            os.path.join(BASE_DIR, 'templates', 'allauth'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'cart.contexts.cart_contents',
            ],
        },
    },
]

# Disable SSL redirect for testing
SECURE_SSL_REDIRECT = False

# Disable session cookie secure flag for testing
SESSION_COOKIE_SECURE = False

# Disable CSRF cookie secure flag for testing
CSRF_COOKIE_SECURE = False 