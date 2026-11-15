from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import GeneroViewSet, ItemBibliotecaViewSet, TituloViewSet

# O Router do DRF gera todas as URLs necessárias para os ViewSets automaticamente
router = DefaultRouter()
router.register(r'generos', GeneroViewSet, basename='genero')
router.register(r'titulos', TituloViewSet, basename='titulo')
router.register(r'biblioteca', ItemBibliotecaViewSet, basename='item-biblioteca')

urlpatterns = [
    path('', include(router.urls)),
]
