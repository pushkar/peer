import os

def get_globals(request):
    return {'ENV_SITE_NAME': os.environ.get('SITE_NAME', 'Peer')}
