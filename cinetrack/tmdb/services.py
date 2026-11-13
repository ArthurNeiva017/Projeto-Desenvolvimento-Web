"""
Cliente da API externa TMDB (The Movie Database).

Documentação oficial: https://developer.themoviedb.org/reference/intro/getting-started

Endpoints consumidos:
  GET /search/movie   - busca de filmes pelo nome
  GET /search/tv      - busca de séries pelo nome
  GET /search/multi   - busca de filmes e séries ao mesmo tempo
  GET /movie/{id}     - detalhes de um filme (gêneros, sinopse, pôster)
  GET /tv/{id}        - detalhes de uma série

A chave (TMDB_API_KEY) fica apenas no servidor, lida do arquivo .env.
O código trata timeout, falha de conexão, resposta inválida e limite de
requisições (HTTP 429), sempre devolvendo uma mensagem amigável (TMDBErro).
"""
import hashlib
import logging

import requests
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

TMDB_BASE_URL = 'https://api.themoviedb.org/3'
TMDB_IMAGEM_URL = 'https://image.tmdb.org/t/p/w342'
TIMEOUT_SEGUNDOS = 5
CACHE_SEGUNDOS = 60 * 10  # reduz chamadas repetidas e ajuda a respeitar o limite do TMDB

# tipo usado no CineTrack -> tipo usado pelo TMDB
TIPOS_TMDB = {'filme': 'movie', 'serie': 'tv'}
TIPOS_CINETRACK = {'movie': 'filme', 'tv': 'serie'}


class TMDBErro(Exception):
    """Falha ao consultar o TMDB. A mensagem pode ser exibida ao usuário."""


class TMDBNaoEncontrado(TMDBErro):
    """O título solicitado não existe no TMDB."""


def _requisitar(caminho, params=None):
    chave = getattr(settings, 'TMDB_API_KEY', '')
    if not chave:
        raise TMDBErro('A integração com o TMDB não está configurada. Use o cadastro manual.')

    params = dict(params or {})
    params['language'] = 'pt-BR'

    # A chave de cache não inclui a chave da API
    assinatura = caminho + '?' + '&'.join(f'{k}={params[k]}' for k in sorted(params))
    chave_cache = 'tmdb:' + hashlib.sha256(assinatura.encode()).hexdigest()
    dados = cache.get(chave_cache)
    if dados is not None:
        return dados

    try:
        resposta = requests.get(
            f'{TMDB_BASE_URL}{caminho}',
            params={**params, 'api_key': chave},
            timeout=TIMEOUT_SEGUNDOS,
        )
    except requests.Timeout:
        logger.warning('TMDB: timeout em %s', caminho)
        raise TMDBErro('O TMDB demorou para responder. Tente novamente em instantes.')
    except requests.RequestException:
        logger.warning('TMDB: falha de conexão em %s', caminho)
        raise TMDBErro('Não foi possível conectar ao TMDB no momento. Tente novamente ou use o cadastro manual.')

    if resposta.status_code == 404:
        raise TMDBNaoEncontrado('Título não encontrado no TMDB.')
    if resposta.status_code == 429:
        logger.warning('TMDB: limite de requisições atingido')
        raise TMDBErro('Muitas consultas ao TMDB em pouco tempo. Aguarde alguns segundos e tente novamente.')
    if resposta.status_code == 401:
        logger.error('TMDB: chave de API inválida ou ausente')
        raise TMDBErro('A integração com o TMDB está indisponível. Use o cadastro manual.')
    if resposta.status_code >= 400:
        logger.error('TMDB: erro HTTP %s em %s', resposta.status_code, caminho)
        raise TMDBErro('O TMDB está indisponível no momento. Tente novamente mais tarde.')

    try:
        dados = resposta.json()
    except ValueError:
        logger.error('TMDB: resposta inválida (não é JSON) em %s', caminho)
        raise TMDBErro('O TMDB retornou uma resposta inválida. Tente novamente mais tarde.')
    if not isinstance(dados, dict):
        raise TMDBErro('O TMDB retornou uma resposta inválida. Tente novamente mais tarde.')

    cache.set(chave_cache, dados, CACHE_SEGUNDOS)
    return dados


def _ano(data):
    """Converte '2021-10-22' em 2021 (ou None)."""
    if data and len(data) >= 4 and data[:4].isdigit():
        return int(data[:4])
    return None


def _normalizar(dado, tipo):
    """Converte um resultado do TMDB para o formato usado pelo CineTrack."""
    poster = dado.get('poster_path')
    return {
        'tmdb_id': dado.get('id'),
        'tipo': tipo,
        'nome': dado.get('title') or dado.get('name') or 'Sem título',
        'ano_lancamento': _ano(dado.get('release_date') or dado.get('first_air_date')),
        'sinopse': dado.get('overview') or '',
        'poster_url': f'{TMDB_IMAGEM_URL}{poster}' if poster else '',
        'generos': [
            {'tmdb_id': g.get('id'), 'nome': g.get('name')}
            for g in dado.get('genres', []) if g.get('id') and g.get('name')
        ],
    }


def buscar_titulos(termo, tipo=''):
    """Busca filmes e/ou séries pelo nome. tipo: 'filme', 'serie' ou '' (ambos)."""
    if tipo in TIPOS_TMDB:
        dados = _requisitar(f'/search/{TIPOS_TMDB[tipo]}', {'query': termo, 'include_adult': 'false'})
        itens = [(r, tipo) for r in dados.get('results', [])]
    else:
        dados = _requisitar('/search/multi', {'query': termo, 'include_adult': 'false'})
        itens = [
            (r, TIPOS_CINETRACK[r.get('media_type')])
            for r in dados.get('results', []) if r.get('media_type') in TIPOS_CINETRACK
        ]
    return [_normalizar(r, t) for r, t in itens if isinstance(r, dict) and r.get('id')]


def detalhar_titulo(tmdb_id, tipo):
    """Busca os detalhes de um filme ou série (inclui gêneros)."""
    if tipo not in TIPOS_TMDB:
        raise TMDBErro('Tipo de título inválido.')
    dados = _requisitar(f'/{TIPOS_TMDB[tipo]}/{int(tmdb_id)}')
    if not dados.get('id'):
        raise TMDBErro('O TMDB retornou uma resposta inválida. Tente novamente mais tarde.')
    return _normalizar(dados, tipo)
