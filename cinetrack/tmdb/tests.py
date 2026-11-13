from unittest.mock import Mock, patch

import requests
from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse

from biblioteca.models import Genero, ItemBiblioteca, Titulo

from .services import TMDBErro, buscar_titulos, detalhar_titulo


def resposta_falsa(status=200, dados=None):
    resposta = Mock()
    resposta.status_code = status
    resposta.json.return_value = dados if dados is not None else {}
    return resposta


DETALHE_DUNA = {
    'id': 438631, 'title': 'Duna', 'release_date': '2021-10-21', 'overview': 'Paul Atreides...',
    'poster_path': '/duna.jpg', 'genres': [{'id': 878, 'name': 'Ficção científica'}],
}


@override_settings(TMDB_API_KEY='chave-de-teste')
class TMDBServiceTests(TestCase):
    def setUp(self):
        cache.clear()

    @patch('tmdb.services.requests.get')
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
    def test_timeout(self, _):
        with self.assertRaisesMessage(TMDBErro, 'demorou'):
            buscar_titulos('duna')

    @patch('tmdb.services.requests.get', side_effect=requests.ConnectionError)
    def test_falha_de_conexao(self, _):
        with self.assertRaisesMessage(TMDBErro, 'conectar'):
            buscar_titulos('duna')

    @patch('tmdb.services.requests.get')
    def test_limite_de_requisicoes(self, mock_get):
        mock_get.return_value = resposta_falsa(status=429)
        with self.assertRaisesMessage(TMDBErro, 'Muitas consultas'):
            buscar_titulos('duna')

    @patch('tmdb.services.requests.get')
    def test_resposta_invalida(self, mock_get):
        resposta = resposta_falsa()
        resposta.json.side_effect = ValueError
        mock_get.return_value = resposta
        with self.assertRaisesMessage(TMDBErro, 'inválida'):
            detalhar_titulo(1, 'filme')

    @override_settings(TMDB_API_KEY='')
    def test_sem_chave_configurada(self):
        with self.assertRaisesMessage(TMDBErro, 'não está configurada'):
            buscar_titulos('duna')


@override_settings(TMDB_API_KEY='chave-de-teste')
class TMDBViewsTests(TestCase):
    def setUp(self):
        cache.clear()
        self.usuario = User.objects.create_user(username='ana', password='SenhaForte#2026')
        self.client.login(username='ana', password='SenhaForte#2026')

    @patch('tmdb.services.requests.get')
    def test_importar_cria_titulo_e_item(self, mock_get):
        mock_get.return_value = resposta_falsa(dados=DETALHE_DUNA)
        resposta = self.client.post(reverse('importar_tmdb'), {'tmdb_id': 438631, 'tipo': 'filme', 'status': 'assistido'})
        item = ItemBiblioteca.objects.get(usuario=self.usuario)
        self.assertRedirects(resposta, reverse('detalhe_item', args=[item.id]))
        self.assertEqual(item.titulo.nome, 'Duna')
        self.assertEqual(item.titulo.genero, Genero.objects.get(tmdb_id=878))
        self.assertEqual(item.status, 'assistido')

    @patch('tmdb.services.requests.get')
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
    def test_importar_com_tmdb_fora_do_ar_oferece_cadastro_manual(self, _):
        resposta = self.client.post(reverse('importar_tmdb'), {'tmdb_id': 1, 'tipo': 'filme', 'status': 'assistido'})
        self.assertRedirects(resposta, reverse('criar_item'))
        self.assertFalse(Titulo.objects.exists())

    @patch('tmdb.services.requests.get', side_effect=requests.ConnectionError)
    def test_busca_com_tmdb_fora_do_ar_mostra_catalogo_local(self, _):
        Titulo.objects.create(nome='Duna', tipo='filme', tmdb_id=438631, genero=Genero.objects.get(nome='Drama'))
        resposta = self.client.get(reverse('buscar_tmdb'), {'q': 'duna'})
        self.assertContains(resposta, 'No catálogo do CineTrack')
        self.assertContains(resposta, 'Duna')
        self.assertContains(resposta, 'indisponíveis')

    def test_busca_termo_curto(self):
        resposta = self.client.get(reverse('buscar_tmdb'), {'q': 'a'})
        self.assertContains(resposta, 'pelo menos 2 caracteres')

    def test_importar_somente_post(self):
        self.assertEqual(self.client.get(reverse('importar_tmdb')).status_code, 405)
