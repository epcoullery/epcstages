# Django settings for epcstages project.
import os

PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEBUG = True

ADMINS = (
    ('Claude Paroz', 'claude@2xlibre.net'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': os.path.join(PROJECT_PATH, 'database.db'), # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
TIME_ZONE = 'Europe/Zurich'

LANGUAGE_CODE = 'fr'

USE_I18N = True
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = False

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(PROJECT_PATH, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(PROJECT_PATH, 'static')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Set it in local_settings.py.
SECRET_KEY = ''

MIDDLEWARE = [
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'common.middleware.LoginRequiredMiddleware',
]

ROOT_URLCONF = 'common.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'common.wsgi.application'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(PROJECT_PATH, 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # Insert your TEMPLATE_CONTEXT_PROCESSORS here or use this
                # list if you haven't customized them:
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',

    'tabimport',
    'stages',
)

FILE_UPLOAD_HANDLERS = ["django.core.files.uploadhandler.TemporaryFileUploadHandler"]

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

ALLOWED_HOSTS = ['localhost', 'stages.pierre-coullery.ch']

# Mapping between column names of a tabular file and Student field names
STUDENT_IMPORT_MAPPING = {
    'NO_CLOEE': 'ext_id',
    'NOM': 'last_name',
    'PRENOM': 'first_name',
    'RUE': 'street',
    'LOCALITE': 'city',  # pcode is separated from city in prepare_import
    'TEL_PRIVE': 'tel',
    'TEL_MOBILE': 'mobile',
    'EMAIL_RPN': 'email',
    'DATENAI': 'birth_date',
    'NAVS13': 'avs',
    'SEXE': 'gender',
    'NO_EMPLOYEUR' : 'corporation',
    'NO_FORMATEUR' : 'instructor',
    'CLASSE_ACTUELLE': 'klass',
}

CORPORATION_IMPORT_MAPPING = {
    'NO_EMPLOYEUR' : 'ext_id',
    'EMPLOYEUR' : 'name',
    'RUE_EMPLOYEUR': 'street',
    'LOCALITE_EMPLOYEUR': 'city',
    'TEL_EMPLOYEUR': 'tel',
    'CANTON_EMPLOYEUR' : 'district',
}

INSTRUCTOR_IMPORT_MAPPING = {
    'NO_FORMATEUR': 'ext_id',
    'NOM_FORMATEUR': 'last_name',
    'PRENOM_FORMATEUR': 'first_name',
    'TEL_FORMATEUR': 'tel',
    'MAIL_FORMATEUR': 'email',
}

CHARGE_SHEET_TITLE = "Feuille de charge pour l'année scolaire 2017-2018"

if 'TRAVIS' in os.environ:
    SECRET_KEY = 'secretkeyfortravistests'
else:
    from .local_settings import *
