import os
import sys

from fabric import task
from invoke import Context, Exit

APP_DIR = '/var/www/epcstages'
VIRTUALENV_DIR = '/var/virtualenvs/stages/bin/activate'

"""Read settings from Django settings"""
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import settings

MAIN_HOST = settings.FABRIC_HOST

@task(hosts=[MAIN_HOST])
def clone_remote_db(conn):
    """
    Copy remote data (JSON dump), download it locally and recreate a local
    SQLite database with those data.
    """
    local = Context()
    db_name = settings.DATABASES['default']['NAME']
    is_sqlite = 'sqlite' in settings.DATABASES['default']['ENGINE']

    def exist_local_db():
        if is_sqlite:
            return os.path.exists(db_name)
        else:  # Assume postgres
            res = local.run('psql --list', hide='stdout')
            return db_name in res.stdout.split()

    if exist_local_db():
        rep = input('A local database named "%s" already exists. Overwrite? (y/n)' % db_name)
        if rep == 'y':
            if is_sqlite:
                os.remove(settings.DATABASES['default']['NAME'])
            else:
                local.run('''sudo -u postgres psql -c "DROP DATABASE %(db)s;"'''  % {'db': db_name})
        else:
            raise Exit("Database not copied")

    # Dump remote data and download the file
    with conn.cd(APP_DIR):
        with conn.prefix('source %s' % VIRTUALENV_DIR):
            conn.run('python manage.py dumpdata --natural-foreign --indent 1 -e auth.Permission auth stages candidats > epcstages.json')
        conn.get('/var/www/epcstages/epcstages.json', None)

    if not is_sqlite:
        local.run(
            '''sudo -u postgres psql -c "CREATE DATABASE %(db)s OWNER=%(owner)s;"''' % {
                'db': db_name, 'owner': settings.DATABASES['default']['USER']
            }
        )

    # Recreate a fresh DB with downloaded data
    local.run("python ../manage.py migrate")
    local.run("python ../manage.py flush --noinput")
    local.run("python ../manage.py loaddata epcstages.json")


@task(hosts=[MAIN_HOST])
def deploy(conn):
    """
    Deploy project with latest Github code
    """
    with conn.cd(APP_DIR):
        conn.run("git pull")
        with conn.prefix('source %s' % VIRTUALENV_DIR):
            conn.run("python manage.py migrate")
            conn.run("python manage.py collectstatic --noinput")
        conn.run("touch common/wsgi.py")

