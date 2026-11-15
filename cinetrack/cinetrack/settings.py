"""
Configurações do projeto CineTrack.

As informações sensíveis (SECRET_KEY e a chave do TMDB) são lidas do arquivo
.env, que não é versionado. Use o arquivo .env.example como modelo.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Caminho base do projeto (pasta que contém o manage.py)
BASE_DIR = Path(__file__).resolve().parent.parent

# Carrega as variáveis do arquivo .env (se existir)
load_dotenv(BASE_DIR / '.env')


# ---------------------------------------------------------------------------
# Segurança
# ---------------------------------------------------------------------------
# A chave secreta vem do .env. O valor padrão serve apenas para rodar localmente.
SECRET_KEY = os.getenv('SECRET_KEY', 'chave-apenas-para-desenvolvimento-local')

# O projeto roda apenas localmente (sem deploy)
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']


# ---------------------------------------------------------------------------
# Aplicativos
# ---------------------------------------------------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Bibliotecas de terceiros
    'rest_framework',
    'rest_framework_simplejwt',
    'drf_spectacular',
    'drf_spectacular_sidecar',
    # Apps do CineTrack
    'contas',
    'biblioteca',
    'tmdb',
    'avaliacoes',
    'relatorios',
    'api',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'cinetrack.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'cinetrack.wsgi.application'


# ---------------------------------------------------------------------------
# Banco de dados (SQLite)
# ---------------------------------------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# ---------------------------------------------------------------------------
# Validação de senha
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
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True


# ---------------------------------------------------------------------------
# Arquivos estáticos (CSS, JavaScript, imagens)
# ---------------------------------------------------------------------------
STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ---------------------------------------------------------------------------
# Autenticação
# ---------------------------------------------------------------------------
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'


# ---------------------------------------------------------------------------
# API externa TMDB (chave obtida em https://www.themoviedb.org/settings/api)
# ---------------------------------------------------------------------------
TMDB_API_KEY = os.getenv('TMDB_API_KEY', '')


# ---------------------------------------------------------------------------
# API REST (Django REST Framework + JWT + Swagger)
# ---------------------------------------------------------------------------
from datetime import timedelta  # noqa: E402

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
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
        'anon': '60/minute',
        'user': '120/minute',
    },
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'AUTH_HEADER_TYPES': ('Bearer',),
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
    'SWAGGER_UI_DIST': 'SIDECAR',
    'SWAGGER_UI_FAVICON_HREF': 'SIDECAR',
    'REDOC_DIST': 'SIDECAR',
}


# ---------------------------------------------------------------------------
# E-mail (exibido no console)
# ---------------------------------------------------------------------------
MAILERS = {
    'default': {
        'BACKEND': 'django.core.mail.backends.console.EmailBackend',
    },
}
