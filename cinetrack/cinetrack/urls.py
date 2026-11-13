"""
Rotas do projeto CineTrack.

O projeto roteia → o app roteia → a view responde.
Cada app possui o seu próprio urls.py, incluído aqui com include().
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('contas.urls')),
    path('biblioteca/', include('biblioteca.urls')),
    path('buscar/', include('tmdb.urls')),
    path('avaliacoes/', include('avaliacoes.urls')),
    path('', include('relatorios.urls')),
]
