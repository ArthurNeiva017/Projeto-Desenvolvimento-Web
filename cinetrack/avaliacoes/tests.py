from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from biblioteca.models import Avaliacao, Genero, ItemBiblioteca, Titulo


class AvaliacoesTests(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user(username='ana', password='SenhaForte#2026')
        titulo = Titulo.objects.create(nome='Bacurau', tipo='filme', genero=Genero.objects.get(nome='Drama'))
        self.item = ItemBiblioteca.objects.create(usuario=self.usuario, titulo=titulo, status='assistido')
        self.client.login(username='ana', password='SenhaForte#2026')

    def test_avaliar_e_alterar(self):
        url = reverse('avaliar_item', args=[self.item.id])
        self.client.post(url, {'nota': 8, 'comentario': 'Muito bom'})
        self.client.post(url, {'nota': 10, 'comentario': 'Excelente'})
        # no máximo uma avaliação por item
        self.assertEqual(Avaliacao.objects.count(), 1)
        self.assertEqual(Avaliacao.objects.get().nota, 10)

    def test_nota_fora_do_intervalo(self):
        resposta = self.client.post(reverse('avaliar_item', args=[self.item.id]), {'nota': 11})
        self.assertEqual(resposta.status_code, 200)
        self.assertFalse(Avaliacao.objects.exists())

    def test_nao_avalia_item_de_outro_usuario(self):
        User.objects.create_user(username='bia', password='SenhaForte#2026')
        self.client.login(username='bia', password='SenhaForte#2026')
        resposta = self.client.post(reverse('avaliar_item', args=[self.item.id]), {'nota': 5})
        self.assertEqual(resposta.status_code, 404)

    def test_excluir_avaliacao(self):
        Avaliacao.objects.create(item_biblioteca=self.item, nota=7)
        self.client.post(reverse('excluir_avaliacao', args=[self.item.id]))
        self.assertFalse(Avaliacao.objects.exists())
