"""
WSGI config for epcstages project.

"""
import os

UPGRADING = False


def upgrade_in_progress(environ, start_response):
    response_headers = [('Content-type','text/html')]
    response = """
        <body>
        <h1>This site is in maintenance mode, please come back in some minutes.</h1>
        <h1>Ce site est actuellement en maintenance, merci de revenir dans quelques minutes.</h1>
        </body>
    """
    if environ['REQUEST_METHOD'] == 'GET':
        status = '200 OK'
    else:
        status = '403 Forbidden'
    start_response(status, response_headers)
    return [response]

if UPGRADING:
    application = upgrade_in_progress
else:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "common.settings")

    # This application object is used by any WSGI server configured to use this
    # file. This includes Django's development server, if the WSGI_APPLICATION
    # setting points here.
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
