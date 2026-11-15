"""
Configurações do projeto CineTrack.

As informações sensíveis (SECRET_KEY e a chave do TMDB) são lidas do arquivo
.env, que não é versionado. Use o arquivo .env.example como modelo.
"""

import os
from pathlib import Path

# python-dotenv: lê o arquivo .env e coloca seus valores nas variáveis de ambiente
from dotenv import load_dotenv

# Caminho base do projeto (pasta que contém o manage.py)
# __file__ = este arquivo; .parent.parent sobe duas pastas (cinetrack/cinetrack → cinetrack)
BASE_DIR = Path(__file__).resolve().parent.parent

# Carrega as variáveis do arquivo .env (se existir)
load_dotenv(BASE_DIR / '.env')


# ---------------------------------------------------------------------------
# Segurança
# ---------------------------------------------------------------------------
# A chave secreta vem do .env. O valor padrão serve apenas para rodar localmente.
# Ela é usada pelo Django para assinar sessões, cookies e tokens (não pode vazar).
SECRET_KEY = os.getenv('SECRET_KEY', 'chave-apenas-para-desenvolvimento-local')

# O projeto roda apenas localmente (sem deploy)
# DEBUG=True mostra páginas de erro detalhadas (nunca usar assim em produção)
DEBUG = True

# Endereços pelos quais o site pode ser acessado
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']


# ---------------------------------------------------------------------------
# Aplicativos
# Cada "app" é um módulo do projeto com seus próprios models, views, urls e templates.
# ---------------------------------------------------------------------------
INSTALLED_APPS = [
    # Apps que já vêm com o Django
    'django.contrib.admin',         # painel administrativo (/admin/)
    'django.contrib.auth',          # usuários, senhas e login
    'django.contrib.contenttypes',
    'django.contrib.sessions',      # sessões (manter o usuário logado)
    'django.contrib.messages',      # mensagens de sucesso/erro entre páginas
    'django.contrib.staticfiles',   # arquivos estáticos (CSS, imagens)
    # Bibliotecas de terceiros
    'rest_framework',               # Django REST Framework (API)
    'rest_framework_simplejwt',     # autenticação da API com tokens JWT
    'drf_spectacular',              # documentação automática da API (OpenAPI)
    'drf_spectacular_sidecar',      # arquivos do Swagger/Redoc servidos localmente
    # Apps do CineTrack
    'contas',       # cadastro, login e logout
    'biblioteca',   # models principais e CRUD da biblioteca
    'tmdb',         # busca e importação de títulos da API do TMDB
    'avaliacoes',   # notas e comentários
    'relatorios',   # dashboard, relatório e exportação CSV
    'api',          # API REST
]

# Middlewares: "camadas" que processam toda requisição antes de chegar na view
# (e toda resposta antes de voltar ao navegador). A ordem importa.
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',            # cabeçalhos de segurança
    'django.contrib.sessions.middleware.SessionMiddleware',     # habilita as sessões
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',                # proteção contra CSRF nos formulários
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # disponibiliza request.user
    'django.contrib.messages.middleware.MessageMiddleware',     # habilita as mensagens
    'django.middleware.clickjacking.XFrameOptionsMiddleware',   # impede o site de ser aberto dentro de iframes
]

# Arquivo principal de rotas do projeto
ROOT_URLCONF = 'cinetrack.urls'

# Configuração dos templates (arquivos HTML)
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Pasta "templates" na raiz: guarda os templates compartilhados (base.html, menu.html...)
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        # APP_DIRS=True: o Django também procura a pasta "templates" dentro de cada app
        'APP_DIRS': True,
        'OPTIONS': {
            # Variáveis disponíveis automaticamente em TODOS os templates
            'context_processors': [
                'django.template.context_processors.request',          # {{ request }}
                'django.contrib.auth.context_processors.auth',          # {{ user }}
                'django.contrib.messages.context_processors.messages',  # {{ messages }}
            ],
        },
    },
]

WSGI_APPLICATION = 'cinetrack.wsgi.application'


# ---------------------------------------------------------------------------
# Banco de dados (SQLite)
# SQLite guarda todo o banco em um único arquivo (db.sqlite3), sem precisar de servidor.
# ---------------------------------------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# ---------------------------------------------------------------------------
# Validação de senha
# Regras aplicadas no cadastro: senha não parecida com o usuário, tamanho mínimo
# (8 caracteres), não estar na lista de senhas comuns e não ser só números.
# ---------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ---------------------------------------------------------------------------
# Internacionalização
# ---------------------------------------------------------------------------
LANGUAGE_CODE = 'pt-br'              # textos do Django (admin, erros) em português
TIME_ZONE = 'America/Sao_Paulo'      # fuso horário de Brasília
USE_I18N = True                      # ativa a tradução
USE_TZ = True                        # datas salvas com fuso horário


# ---------------------------------------------------------------------------
# Arquivos estáticos (CSS, JavaScript, imagens)
# ---------------------------------------------------------------------------
STATIC_URL = 'static/'               # endereço base: /static/css/style.css
STATICFILES_DIRS = [
    BASE_DIR / 'static',             # pasta onde ficam os arquivos estáticos do projeto
]

# Tipo padrão da chave primária (id) criada automaticamente nos models
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ---------------------------------------------------------------------------
# Autenticação
# ---------------------------------------------------------------------------
LOGIN_URL = 'login'                  # para onde o @login_required envia quem não está logado
LOGIN_REDIRECT_URL = 'dashboard'     # para onde ir depois do login
LOGOUT_REDIRECT_URL = 'login'        # para onde ir depois do logout


# ---------------------------------------------------------------------------
# API externa TMDB (chave obtida em https://www.themoviedb.org/settings/api)
# ---------------------------------------------------------------------------
TMDB_API_KEY = os.getenv('TMDB_API_KEY', '')


# ---------------------------------------------------------------------------
# API REST (Django REST Framework + JWT + Swagger)
# ---------------------------------------------------------------------------
from datetime import timedelta  # noqa: E402

REST_FRAMEWORK = {
    # A API identifica o usuário pelo token JWT enviado no cabeçalho Authorization
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    # Padrão: qualquer um pode LER (GET); para alterar dados é preciso estar autenticado
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ),
    # Define o drf-spectacular como a classe geradora de esquema padrão
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    # Paginação: 10 registros por página (?page=2)
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    # Rate limiting: retorna HTTP 429 quando o limite é ultrapassado
    'DEFAULT_THROTTLE_CLASSES': (
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ),
    'DEFAULT_THROTTLE_RATES': {
        'anon': '60/minute',    # visitantes sem login: 60 requisições por minuto
        'user': '120/minute',   # usuários autenticados: 120 requisições por minuto
    },
}

# Configuração dos tokens JWT
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),   # token de acesso vale 5 minutos
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),     # token de renovação vale 1 dia
    'AUTH_HEADER_TYPES': ('Bearer',),                # formato: "Authorization: Bearer <token>"
}

# Configurações customizadas do Swagger/OpenAPI
SPECTACULAR_SETTINGS = {
    'TITLE': 'API do CineTrack',
    'DESCRIPTION': (
        'API REST do CineTrack. As rotas de catálogo (gêneros e títulos) são públicas e somente leitura. '
        'As rotas de biblioteca exigem autenticação JWT: obtenha o token em POST /api/token/ e envie '
        'o cabeçalho Authorization: Bearer <access>.'
    ),
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    # 'SIDECAR': os arquivos do Swagger/Redoc vêm do pacote instalado, não de uma CDN externa
    'SWAGGER_UI_DIST': 'SIDECAR',
    'SWAGGER_UI_FAVICON_HREF': 'SIDECAR',
    'REDOC_DIST': 'SIDECAR',
}


# ---------------------------------------------------------------------------
# E-mail (exibido no console)
# Em vez de enviar e-mails de verdade, o conteúdo é impresso no terminal
# ---------------------------------------------------------------------------
MAILERS = {
    'default': {
        'BACKEND': 'django.core.mail.backends.console.EmailBackend',
    },
}
