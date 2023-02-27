import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

'''
This file should be placed in the same folder as settings.py
'''



DEBUG = False

# ec2_health_check = os.environ.get('EC2_PRV_IP')
ALLOWED_HOSTS = ['18.195.219.19']

#dbs

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('POSTGRES_DB'), 
        'USER': os.environ.get('POSTGRES_USER'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
        'HOST': os.environ.get('HOST'),
        'PORT': '5432',
    }
}

# static

STATIC_ROOT = '/var/www/hex_ocean/static'
STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
MEDIA_URL = 'media/'
MEDIA_ROOT = '/var/www/hex_ocean/media'

# logs

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'debug.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
