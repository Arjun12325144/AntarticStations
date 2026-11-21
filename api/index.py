import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
from django.core.wsgi import get_wsgi_application
from django.core.management import call_command

app = get_wsgi_application()
if os.environ.get('VERCEL'):          # fresh /tmp database on every cold start
    call_command('migrate', verbosity=0)
    call_command('seed')
