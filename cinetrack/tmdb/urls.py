from django.urls import path
from . import views

urlpatterns = [
    path('', views.buscar_tmdb, name='buscar_tmdb'),
    path('importar/', views.importar_tmdb, name='importar_tmdb'),
    path('adicionar/', views.adicionar_do_catalogo, name='adicionar_do_catalogo'),
]
