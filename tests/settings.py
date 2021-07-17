import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SECRET_KEY = ')dajq1#olz2*y&$1x0y&pd0ev-a_h2*j%ed0j5ych2^oy%*2%e'

DATETIME_INPUT_FORMATS = ('%Y-%m-%dT%H:%M:%S%z',)

INSTALLED_APPS = (
    'django.contrib.contenttypes',
    'django_api_forms',
    'tests.testapp',
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'
