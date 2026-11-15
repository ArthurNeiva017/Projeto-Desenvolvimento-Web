"""
Rotas do projeto CineTrack.

O projeto roteia → o app roteia → a view responde.
Cada app possui o seu próprio urls.py, incluído aqui com include().
"""
from django.contrib import admin
from django.urls import path, include
# Views prontas que geram a documentação da API
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
# Views prontas que geram (e renovam) os tokens JWT
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# Lista de rotas principais. O Django percorre esta lista de cima para baixo
# e usa a primeira rota que combinar com o endereço acessado.
urlpatterns = [
    path('admin/', admin.site.urls),                  # painel administrativo
    path('', include('contas.urls')),                 # /, /login/, /logout/, /register/
    path('biblioteca/', include('biblioteca.urls')),  # CRUD da biblioteca
    path('buscar/', include('tmdb.urls')),            # busca e importação do TMDB
    path('avaliacoes/', include('avaliacoes.urls')),  # avaliações
    path('', include('relatorios.urls')),             # /dashboard/, /relatorio/

    # --- API REST (versão 1) ---
    path('api/v1/', include('api.urls')),
    # POST com usuário e senha → devolve os tokens "access" e "refresh"
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # POST com o token "refresh" → devolve um novo token "access"
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # --- Documentação da API ---
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),  # esquema OpenAPI (arquivo YAML)
    path('api/docs/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),  # tela interativa
    path('api/docs/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),           # documentação em leitura
]
