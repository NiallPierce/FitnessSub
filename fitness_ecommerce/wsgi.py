"""
WSGI config for fitness_ecommerce project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
from pathlib import Path
from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitness_ecommerce.settings')

application = get_wsgi_application()
BASE_DIR = Path(__file__).resolve().parent.parent

# Configure WhiteNoise
application = WhiteNoise(
    application,
    root=os.path.join(BASE_DIR, 'staticfiles'),
    prefix='static/',
    max_age=31536000,  # 1 year
    add_headers_function=lambda headers, path, url: headers.update({
        'Cache-Control': 'public, max-age=31536000',
    })
)
