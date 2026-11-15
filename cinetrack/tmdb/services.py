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
import hashlib  # gera um "resumo" (hash) de um texto; usado para montar a chave do cache
import logging  # registra avisos/erros no terminal do servidor (para os desenvolvedores)

import requests  # biblioteca para fazer requisições HTTP a outros sites/APIs
from django.conf import settings
from django.core.cache import cache  # cache do Django: guarda respostas por um tempo, evitando repetir chamadas

# Logger deste módulo: as mensagens aparecem identificadas como "tmdb.services"
logger = logging.getLogger(__name__)

# Constantes de configuração da integração
TMDB_BASE_URL = 'https://api.themoviedb.org/3'          # endereço base da API
TMDB_IMAGEM_URL = 'https://image.tmdb.org/t/p/w342'     # endereço base dos pôsteres (largura 342px)
TIMEOUT_SEGUNDOS = 5   # tempo máximo de espera pela resposta do TMDB
CACHE_SEGUNDOS = 60 * 10  # reduz chamadas repetidas e ajuda a respeitar o limite do TMDB

# tipo usado no CineTrack -> tipo usado pelo TMDB
TIPOS_TMDB = {'filme': 'movie', 'serie': 'tv'}
# tipo usado pelo TMDB -> tipo usado no CineTrack (o caminho inverso)
TIPOS_CINETRACK = {'movie': 'filme', 'tv': 'serie'}


# Exceções (erros) personalizadas. Criar nossas próprias exceções permite que as
# views capturem "qualquer problema com o TMDB" com um único except TMDBErro.
class TMDBErro(Exception):
    """Falha ao consultar o TMDB. A mensagem pode ser exibida ao usuário."""


# Herda de TMDBErro: é um tipo mais específico de erro (título inexistente)
class TMDBNaoEncontrado(TMDBErro):
    """O título solicitado não existe no TMDB."""


# Função central que faz TODAS as chamadas HTTP ao TMDB.
# O "_" no início do nome indica que é de uso interno deste arquivo.
def _requisitar(caminho, params=None):
    # Lê a chave da API das configurações (que por sua vez vem do arquivo .env)
    chave = getattr(settings, 'TMDB_API_KEY', '')
    if not chave:
        raise TMDBErro('A integração com o TMDB não está configurada. Use o cadastro manual.')

    # Copia os parâmetros (para não alterar o dicionário original) e pede respostas em português
    params = dict(params or {})
    params['language'] = 'pt-BR'

    # A chave de cache não inclui a chave da API
    # Monta um texto único para esta consulta (ex.: "/search/movie?language=pt-BR&query=duna")
    # e transforma em hash SHA-256 para usar como identificador no cache
    assinatura = caminho + '?' + '&'.join(f'{k}={params[k]}' for k in sorted(params))
    chave_cache = 'tmdb:' + hashlib.sha256(assinatura.encode()).hexdigest()
    # Se essa mesma consulta foi feita há pouco tempo, devolve a resposta guardada (sem chamar o TMDB)
    dados = cache.get(chave_cache)
    if dados is not None:
        return dados

    # Faz a requisição GET ao TMDB. try/except captura problemas de rede
    try:
        resposta = requests.get(
            f'{TMDB_BASE_URL}{caminho}',
            params={**params, 'api_key': chave},  # junta os parâmetros com a chave da API
            timeout=TIMEOUT_SEGUNDOS,             # não espera para sempre
        )
    except requests.Timeout:
        # O TMDB demorou mais que 5 segundos
        logger.warning('TMDB: timeout em %s', caminho)
        raise TMDBErro('O TMDB demorou para responder. Tente novamente em instantes.')
    except requests.RequestException:
        # Qualquer outra falha de rede (sem internet, DNS, conexão recusada...)
        logger.warning('TMDB: falha de conexão em %s', caminho)
        raise TMDBErro('Não foi possível conectar ao TMDB no momento. Tente novamente ou use o cadastro manual.')

    # Trata os códigos de status HTTP de erro, transformando cada um em mensagem amigável
    if resposta.status_code == 404:   # não encontrado
        raise TMDBNaoEncontrado('Título não encontrado no TMDB.')
    if resposta.status_code == 429:   # muitas requisições em pouco tempo (rate limit)
        logger.warning('TMDB: limite de requisições atingido')
        raise TMDBErro('Muitas consultas ao TMDB em pouco tempo. Aguarde alguns segundos e tente novamente.')
    if resposta.status_code == 401:   # não autorizado (chave inválida)
        logger.error('TMDB: chave de API inválida ou ausente')
        raise TMDBErro('A integração com o TMDB está indisponível. Use o cadastro manual.')
    if resposta.status_code >= 400:   # qualquer outro erro (4xx ou 5xx)
        logger.error('TMDB: erro HTTP %s em %s', resposta.status_code, caminho)
        raise TMDBErro('O TMDB está indisponível no momento. Tente novamente mais tarde.')

    # Converte o corpo da resposta de JSON para dicionário Python
    try:
        dados = resposta.json()
    except ValueError:
        logger.error('TMDB: resposta inválida (não é JSON) em %s', caminho)
        raise TMDBErro('O TMDB retornou uma resposta inválida. Tente novamente mais tarde.')
    # Garante que veio um objeto JSON (dicionário), que é o formato esperado
    if not isinstance(dados, dict):
        raise TMDBErro('O TMDB retornou uma resposta inválida. Tente novamente mais tarde.')

    # Guarda a resposta no cache por 10 minutos e devolve
    cache.set(chave_cache, dados, CACHE_SEGUNDOS)
    return dados


def _ano(data):
    """Converte '2021-10-22' em 2021 (ou None)."""
    # data[:4] pega os 4 primeiros caracteres (o ano); isdigit() confere se são números
    if data and len(data) >= 4 and data[:4].isdigit():
        return int(data[:4])
    return None


def _normalizar(dado, tipo):
    """Converte um resultado do TMDB para o formato usado pelo CineTrack."""
    # O TMDB usa nomes de campos diferentes para filmes e séries
    # (ex.: "title" x "name", "release_date" x "first_air_date"), então padronizamos aqui
    poster = dado.get('poster_path')
    return {
        'tmdb_id': dado.get('id'),
        'tipo': tipo,
        'nome': dado.get('title') or dado.get('name') or 'Sem título',
        'ano_lancamento': _ano(dado.get('release_date') or dado.get('first_air_date')),
        'sinopse': dado.get('overview') or '',
        # O TMDB devolve só o final do caminho da imagem; juntamos com o endereço base
        'poster_url': f'{TMDB_IMAGEM_URL}{poster}' if poster else '',
        # Lista de gêneros, ignorando os que vierem sem id ou sem nome
        'generos': [
            {'tmdb_id': g.get('id'), 'nome': g.get('name')}
            for g in dado.get('genres', []) if g.get('id') and g.get('name')
        ],
    }


def buscar_titulos(termo, tipo=''):
    """Busca filmes e/ou séries pelo nome. tipo: 'filme', 'serie' ou '' (ambos)."""
    if tipo in TIPOS_TMDB:
        # Tipo escolhido: usa /search/movie ou /search/tv
        dados = _requisitar(f'/search/{TIPOS_TMDB[tipo]}', {'query': termo, 'include_adult': 'false'})
        # Lista de pares (resultado, tipo)
        itens = [(r, tipo) for r in dados.get('results', [])]
    else:
        # Sem tipo: usa /search/multi, que também retorna pessoas; por isso
        # mantemos apenas os resultados do tipo "movie" ou "tv"
        dados = _requisitar('/search/multi', {'query': termo, 'include_adult': 'false'})
        itens = [
            (r, TIPOS_CINETRACK[r.get('media_type')])
            for r in dados.get('results', []) if r.get('media_type') in TIPOS_CINETRACK
        ]
    # Converte cada resultado válido para o formato do CineTrack
    return [_normalizar(r, t) for r, t in itens if isinstance(r, dict) and r.get('id')]


def detalhar_titulo(tmdb_id, tipo):
    """Busca os detalhes de um filme ou série (inclui gêneros)."""
    if tipo not in TIPOS_TMDB:
        raise TMDBErro('Tipo de título inválido.')
    # int(tmdb_id) garante que só números entram no endereço da requisição
    dados = _requisitar(f'/{TIPOS_TMDB[tipo]}/{int(tmdb_id)}')
    if not dados.get('id'):
        raise TMDBErro('O TMDB retornou uma resposta inválida. Tente novamente mais tarde.')
    return _normalizar(dados, tipo)
