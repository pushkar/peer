import os

def get_globals(request):
    return {'ENV_SITE_NAME': os.getenv('SITE_NAME', 'Peer')}
