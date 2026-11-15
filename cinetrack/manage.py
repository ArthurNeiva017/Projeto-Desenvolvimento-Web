#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
# Utilitário de linha de comando do Django. Exemplos de uso:
#   python manage.py runserver      -> inicia o servidor local (http://127.0.0.1:8000)
#   python manage.py migrate        -> cria/atualiza as tabelas do banco
#   python manage.py test           -> roda os testes automatizados
#   python manage.py createsuperuser -> cria um administrador para o /admin/
import os
import sys


def main():
    """Run administrative tasks."""
    # Informa ao Django qual arquivo de configurações usar
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cinetrack.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    # Executa o comando digitado no terminal (sys.argv = argumentos da linha de comando)
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
