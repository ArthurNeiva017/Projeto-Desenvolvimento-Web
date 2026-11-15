# Configuração do app (o Django lê esta classe ao iniciar o projeto)
from django.apps import AppConfig


class AvaliacoesConfig(AppConfig):
    # name: nome do app (o mesmo usado em INSTALLED_APPS no settings.py)
    name = 'avaliacoes'
    # verbose_name: nome amigável exibido no painel admin
    verbose_name = 'Avaliações'
