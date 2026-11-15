# Configuração do app (o Django lê esta classe ao iniciar o projeto)
from django.apps import AppConfig


class TmdbConfig(AppConfig):
    # name: nome do app (o mesmo usado em INSTALLED_APPS no settings.py)
    name = 'tmdb'
    # verbose_name: nome amigável exibido no painel admin
    verbose_name = 'Integração com o TMDB'
