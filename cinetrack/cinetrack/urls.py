"""
Rotas do projeto CineTrack.

O projeto roteia → o app roteia → a view responde.
Cada app possui o seu próprio urls.py, incluído aqui com include().
"""
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('contas.urls')),
    path('biblioteca/', include('biblioteca.urls')),
    path('buscar/', include('tmdb.urls')),
    path('avaliacoes/', include('avaliacoes.urls')),
    path('', include('relatorios.urls')),

    # --- API REST (versão 1) ---
    path('api/v1/', include('api.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # --- Documentação da API ---
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/docs/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
