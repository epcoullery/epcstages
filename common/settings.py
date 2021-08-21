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
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(PROJECT_PATH, 'database.db'),
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

TIME_ZONE = 'Europe/Zurich'

LANGUAGE_CODE = 'fr'

USE_I18N = True
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = False

# Absolute filesystem path to the directory that will hold user-uploaded files.
MEDIA_ROOT = os.path.join(PROJECT_PATH, 'media')
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
STATIC_ROOT = os.path.join(PROJECT_PATH, 'static')
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

    'django_summernote',
    'tabimport',
    'stages.apps.StagesConfig',
    'candidats',
)

FILE_UPLOAD_HANDLERS = ["django.core.files.uploadhandler.TemporaryFileUploadHandler"]

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

ALLOWED_HOSTS = ['localhost', 'stages.pierre-coullery.ch']

# candidats admin shows confirmation_date readonly field twice.
SILENCED_SYSTEM_CHECKS = ['admin.E012']

SUMMERNOTE_CONFIG = {
    'summernote': {
        'toolbar': [
            # [groupName, [list of button]]
            ['style', ['bold', 'italic', 'underline', 'clear']],
            ['font', ['strikethrough']],
            ['fontsize', ['fontsize']],
            ['color', ['color']],
            ['para', ['ul', 'ol', 'paragraph']],
        ]
    }
}

FABRIC_HOST = 'gestion.pierre-coullery.ch'
FABRIC_USERNAME = ''

INSTRUCTOR_IMPORT_MAPPING = {
    'NO_FORMATEUR': 'ext_id',
    'NOM_FORMATEUR': 'last_name',
    'PRENOM_FORMATEUR': 'first_name',
    'TEL_FORMATEUR': 'tel',
    'MAIL_FORMATEUR': 'email',
}

CHARGE_SHEET_TITLE = "Feuille de charge pour l'année scolaire 2018-2019"
PDF_FOOTER_TEXT = 'Ecole Santé-social Pierre-Coullery | Prévoyance 82 - 2300 La Chaux-de-Fonds | 032 886 33 00 | cifom-epc@rpn.ch'

# Maximum numbers of periods per teacher per year
MAX_ENS_PERIODS = 1900
MAX_ENS_FORMATION = 250
GLOBAL_CHARGE_TOTAL = 2150
GLOBAL_CHARGE_PERCENT = 21.5

RESP_FILIERE_EDE = ("Ann Schaub-Murray", 'F')
DATE_LIEU_EXAMEN_EDE = "mercredi 7 mars 2018, à 13h30, salle A405"
RESP_FILIERE_EDS = ("Brahim Ali Hemma", 'M')

if 'TRAVIS' in os.environ:
    SECRET_KEY = 'secretkeyfortravistests'
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
else:
    from .local_settings import *
