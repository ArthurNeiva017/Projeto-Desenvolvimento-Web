"""
WSGI config for cinetrack project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cinetrack.settings')

# Ponto de entrada usado por servidores WSGI para executar o projeto em produção.
# Para rodar localmente usamos "python manage.py runserver", que não precisa deste arquivo.
application = get_wsgi_application()
