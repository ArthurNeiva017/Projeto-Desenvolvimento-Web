# Testes automatizados da integração com o TMDB.
# As chamadas à API real são SIMULADAS com "mock" (patch), então os testes
# não dependem de internet nem da chave da API.
# Executar com: python manage.py test
# Cada método que começa com "test_" é um caso de teste. O Django cria um banco
# de dados temporário só para os testes, que é apagado no final.
from unittest.mock import Mock, patch

import requests
from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse

from biblioteca.models import Genero, ItemBiblioteca, Titulo

from .services import TMDBErro, buscar_titulos, detalhar_titulo


# Cria uma resposta HTTP "falsa" (Mock) para simular o TMDB nos testes
def resposta_falsa(status=200, dados=None):
    resposta = Mock()
    resposta.status_code = status
    resposta.json.return_value = dados if dados is not None else {}
    return resposta


# Exemplo de resposta do TMDB com os detalhes de um filme
DETALHE_DUNA = {
    'id': 438631, 'title': 'Duna', 'release_date': '2021-10-21', 'overview': 'Paul Atreides...',
    'poster_path': '/duna.jpg', 'genres': [{'id': 878, 'name': 'Ficção científica'}],
}


# override_settings troca a chave da API somente durante os testes
@override_settings(TMDB_API_KEY='chave-de-teste')
class TMDBServiceTests(TestCase):
    # setUp roda ANTES de cada teste: prepara os dados necessários
    def setUp(self):
        cache.clear()

    @patch('tmdb.services.requests.get')
    # Teste: A busca converte os dados do TMDB para o formato do CineTrack e ignora resultados de pessoas
    def test_busca_normaliza_resultados(self, mock_get):
        mock_get.return_value = resposta_falsa(dados={'results': [
            {'id': 1, 'media_type': 'movie', 'title': 'Duna', 'release_date': '2021-10-21', 'poster_path': '/a.jpg'},
            {'id': 2, 'media_type': 'tv', 'name': 'Dark', 'first_air_date': '2017-12-01'},
            {'id': 3, 'media_type': 'person', 'name': 'Ator'},
        ]})
        resultados = buscar_titulos('du')
        self.assertEqual(len(resultados), 2)
        self.assertEqual(resultados[0]['tipo'], 'filme')
        self.assertEqual(resultados[0]['ano_lancamento'], 2021)
        self.assertTrue(resultados[0]['poster_url'].startswith('https://image.tmdb.org/'))
        self.assertEqual(resultados[1]['tipo'], 'serie')
        # timeout sempre informado
        self.assertEqual(mock_get.call_args.kwargs['timeout'], 5)

    @patch('tmdb.services.requests.get', side_effect=requests.Timeout)
    # Teste: Se o TMDB demorar demais, é lançado um TMDBErro com mensagem amigável
    def test_timeout(self, _):
        with self.assertRaisesMessage(TMDBErro, 'demorou'):
            buscar_titulos('duna')

    @patch('tmdb.services.requests.get', side_effect=requests.ConnectionError)
    # Teste: Falha de conexão gera TMDBErro com mensagem amigável
    def test_falha_de_conexao(self, _):
        with self.assertRaisesMessage(TMDBErro, 'conectar'):
            buscar_titulos('duna')

    @patch('tmdb.services.requests.get')
    # Teste: Resposta 429 (limite de requisições) gera mensagem específica
    def test_limite_de_requisicoes(self, mock_get):
        mock_get.return_value = resposta_falsa(status=429)
        with self.assertRaisesMessage(TMDBErro, 'Muitas consultas'):
            buscar_titulos('duna')

    @patch('tmdb.services.requests.get')
    # Teste: Resposta que não é JSON gera mensagem de resposta inválida
    def test_resposta_invalida(self, mock_get):
        resposta = resposta_falsa()
        resposta.json.side_effect = ValueError
        mock_get.return_value = resposta
        with self.assertRaisesMessage(TMDBErro, 'inválida'):
            detalhar_titulo(1, 'filme')

    @override_settings(TMDB_API_KEY='')
    # Teste: Sem chave da API configurada, avisa que a integração não está configurada
    def test_sem_chave_configurada(self):
        with self.assertRaisesMessage(TMDBErro, 'não está configurada'):
            buscar_titulos('duna')


@override_settings(TMDB_API_KEY='chave-de-teste')
class TMDBViewsTests(TestCase):
    # setUp roda ANTES de cada teste: prepara os dados necessários
    def setUp(self):
        cache.clear()
        self.usuario = User.objects.create_user(username='ana', password='SenhaForte#2026')
        self.client.login(username='ana', password='SenhaForte#2026')

    @patch('tmdb.services.requests.get')
    # Teste: Importar do TMDB cria o título (com o gênero correto) e o item na biblioteca
    def test_importar_cria_titulo_e_item(self, mock_get):
        mock_get.return_value = resposta_falsa(dados=DETALHE_DUNA)
        resposta = self.client.post(reverse('importar_tmdb'), {'tmdb_id': 438631, 'tipo': 'filme', 'status': 'assistido'})
        item = ItemBiblioteca.objects.get(usuario=self.usuario)
        self.assertRedirects(resposta, reverse('detalhe_item', args=[item.id]))
        self.assertEqual(item.titulo.nome, 'Duna')
        self.assertEqual(item.titulo.genero, Genero.objects.get(tmdb_id=878))
        self.assertEqual(item.status, 'assistido')

    @patch('tmdb.services.requests.get')
    # Teste: Importar o mesmo título duas vezes não duplica e leva para a edição
    def test_importar_duas_vezes_oferece_edicao(self, mock_get):
        mock_get.return_value = resposta_falsa(dados=DETALHE_DUNA)
        dados = {'tmdb_id': 438631, 'tipo': 'filme', 'status': 'assistido'}
        self.client.post(reverse('importar_tmdb'), dados)
        resposta = self.client.post(reverse('importar_tmdb'), dados)
        item = ItemBiblioteca.objects.get(usuario=self.usuario)
        self.assertRedirects(resposta, reverse('editar_item', args=[item.id]))
        self.assertEqual(Titulo.objects.count(), 1)
        # o título reaproveitado do catálogo não chama o TMDB de novo
        self.assertEqual(mock_get.call_count, 1)

    @patch('tmdb.services.requests.get', side_effect=requests.Timeout)
    # Teste: Com o TMDB fora do ar, a importação redireciona para o cadastro manual
    def test_importar_com_tmdb_fora_do_ar_oferece_cadastro_manual(self, _):
        resposta = self.client.post(reverse('importar_tmdb'), {'tmdb_id': 1, 'tipo': 'filme', 'status': 'assistido'})
        self.assertRedirects(resposta, reverse('criar_item'))
        self.assertFalse(Titulo.objects.exists())

    @patch('tmdb.services.requests.get', side_effect=requests.ConnectionError)
    # Teste: Com o TMDB fora do ar, a busca ainda mostra os resultados do catálogo local
    def test_busca_com_tmdb_fora_do_ar_mostra_catalogo_local(self, _):
        Titulo.objects.create(nome='Duna', tipo='filme', tmdb_id=438631, genero=Genero.objects.get(nome='Drama'))
        resposta = self.client.get(reverse('buscar_tmdb'), {'q': 'duna'})
        self.assertContains(resposta, 'No catálogo do CineTrack')
        self.assertContains(resposta, 'Duna')
        self.assertContains(resposta, 'indisponíveis')

    # Teste: Termo de busca com menos de 2 caracteres é rejeitado
    def test_busca_termo_curto(self):
        resposta = self.client.get(reverse('buscar_tmdb'), {'q': 'a'})
        self.assertContains(resposta, 'pelo menos 2 caracteres')

    # Teste: A rota de importar só aceita POST (GET retorna 405)
    def test_importar_somente_post(self):
        self.assertEqual(self.client.get(reverse('importar_tmdb')).status_code, 405)
