# Configuração do app (o Django lê esta classe ao iniciar o projeto)
from django.apps import AppConfig


class ContasConfig(AppConfig):
    # name: nome do app (o mesmo usado em INSTALLED_APPS no settings.py)
    name = 'contas'
    # verbose_name: nome amigável exibido no painel admin
    verbose_name = 'Contas de usuário'
