# Rotas do app tmdb (prefixo "buscar/" definido no urls.py do projeto)
from django.urls import path
from . import views

urlpatterns = [
    path('', views.buscar_tmdb, name='buscar_tmdb'),                                # /buscar/  → tela de busca
    path('importar/', views.importar_tmdb, name='importar_tmdb'),                   # /buscar/importar/  → importa do TMDB (POST)
    path('adicionar/', views.adicionar_do_catalogo, name='adicionar_do_catalogo'),  # /buscar/adicionar/ → adiciona do catálogo local (POST)
]
