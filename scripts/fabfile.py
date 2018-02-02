# -*- coding: utf-8 -*-
import os
import sys

from fabric.api import cd, env, get, local, prefix, prompt, run
from fabric.contrib import django
from fabric.utils import abort

APP_DIR = '/var/www/epcstages'
VIRTUALENV_DIR = '/var/virtualenvs/stages/bin/activate'

"""Read settings from Django settings"""
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
django.settings_module('common.settings')
from common import settings

env.hosts = [settings.FABRIC_HOST]
env.user = settings.FABRIC_USERNAME


def clone_remote_db():
    """
    Copy remote data (JSON dump), download it locally and recreate a local
    SQLite database with those data.
    """
    db_name = settings.DATABASES['default']['NAME']
    is_sqlite = 'sqlite' in settings.DATABASES['default']['ENGINE']

    def exist_local_db():
        if is_sqlite:
            return os.path.exists(db_name)
        else:  # Assume postgres
            db_list = local('psql --list', capture=True)
            return (' ' + db_name + ' ') in db_list

    if exist_local_db():
        rep = prompt('A local database named "%s" already exists. Overwrite? (y/n)' % db_name)
        if rep == 'y':
            if is_sqlite:
                os.remove(settings.DATABASES['default']['NAME'])
            else:
                local('''sudo -u postgres psql -c "DROP DATABASE %(db)s;"'''  % {'db': db_name})
        else:
            abort("Database not copied")

    # Dump remote data and download the file
    with cd(APP_DIR):
        with prefix('source %s' % VIRTUALENV_DIR):
            run('python manage.py dumpdata --natural-foreign --indent 1 -e auth.Permission auth stages candidats > epcstages.json')
        get('epcstages.json', '.')

    if not is_sqlite:
        local('''sudo -u postgres psql -c "CREATE DATABASE %(db)s OWNER=%(owner)s;"''' % {
        'db': db_name, 'owner': settings.DATABASES['default']['USER']})

    # Recreate a fresh DB with downloaded data
    local("python ../manage.py migrate")
    local("python ../manage.py flush --noinput")
    local("python ../manage.py loaddata epcstages.json")


def deploy():
    """
    Deploy project with latest Github code
    """
    with cd(APP_DIR):
        run("git pull")
        with prefix('source %s' % VIRTUALENV_DIR):
            run("python manage.py migrate")
            run("python manage.py collectstatic --noinput")
        run("touch common/wsgi.py")

