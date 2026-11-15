# Rotas da API REST (prefixo "api/v1/" definido no urls.py do projeto)
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import GeneroViewSet, ItemBibliotecaViewSet, TituloViewSet

# O Router do DRF gera todas as URLs necessárias para os ViewSets automaticamente
# Ex.: para "biblioteca" ele cria /biblioteca/ (listar/criar) e /biblioteca/{id}/ (detalhar/alterar/excluir)
router = DefaultRouter()
router.register(r'generos', GeneroViewSet, basename='genero')                     # /api/v1/generos/
router.register(r'titulos', TituloViewSet, basename='titulo')                     # /api/v1/titulos/
router.register(r'biblioteca', ItemBibliotecaViewSet, basename='item-biblioteca') # /api/v1/biblioteca/

urlpatterns = [
    path('', include(router.urls)),  # inclui todas as rotas geradas pelo router
]
