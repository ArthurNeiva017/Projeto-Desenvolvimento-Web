from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Avaliacao, Genero, ItemBiblioteca, Titulo


class BibliotecaTests(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user(username='ana', password='SenhaForte#2026')
        self.outro = User.objects.create_user(username='bia', password='SenhaForte#2026')
        self.genero = Genero.objects.get(nome='Drama')  # criado pela migration de dados
        self.titulo = Titulo.objects.create(nome='Central do Brasil', tipo='filme', genero=self.genero, ano_lancamento=1998)
        self.item = ItemBiblioteca.objects.create(usuario=self.usuario, titulo=self.titulo)
        self.client.login(username='ana', password='SenhaForte#2026')

    def test_lista_exige_login(self):
        self.client.logout()
        resposta = self.client.get(reverse('lista_biblioteca'))
        self.assertEqual(resposta.status_code, 302)
        self.assertIn(reverse('login'), resposta.url)

    def test_lista_mostra_apenas_itens_do_usuario(self):
        outro_titulo = Titulo.objects.create(nome='Bacurau', tipo='filme', genero=self.genero)
        ItemBiblioteca.objects.create(usuario=self.outro, titulo=outro_titulo)
        resposta = self.client.get(reverse('lista_biblioteca'))
        self.assertContains(resposta, 'Central do Brasil')
        self.assertNotContains(resposta, 'Bacurau')

    def test_busca_por_nome_e_status(self):
        resposta = self.client.get(reverse('lista_biblioteca'), {'q': 'central', 'status': 'quero_assistir'})
        self.assertContains(resposta, 'Central do Brasil')
        resposta = self.client.get(reverse('lista_biblioteca'), {'q': 'central', 'status': 'assistido'})
        self.assertNotContains(resposta, 'Central do Brasil')

    def test_criar_item(self):
        resposta = self.client.post(reverse('criar_item'), {
            'nome': 'Cidade de Deus', 'tipo': 'filme', 'genero': self.genero.id,
            'ano_lancamento': 2002, 'sinopse': '', 'poster_url': '', 'status': 'assistido',
        })
        self.assertRedirects(resposta, reverse('lista_biblioteca'))
        self.assertTrue(ItemBiblioteca.objects.filter(usuario=self.usuario, titulo__nome='Cidade de Deus', status='assistido').exists())

    def test_criar_item_invalido(self):
        resposta = self.client.post(reverse('criar_item'), {
            'nome': 'X', 'tipo': 'filme', 'genero': self.genero.id, 'ano_lancamento': 1500, 'status': 'assistido',
        })
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, 'pelo menos 2 caracteres')
        self.assertContains(resposta, 'Informe um ano entre 1888')

    def test_editar_item_manual(self):
        resposta = self.client.post(reverse('editar_item', args=[self.item.id]), {
            'nome': 'Central do Brasil', 'tipo': 'filme', 'genero': self.genero.id,
            'ano_lancamento': 1998, 'status': 'assistindo',
        })
        self.assertRedirects(resposta, reverse('detalhe_item', args=[self.item.id]))
        self.item.refresh_from_db()
        self.assertEqual(self.item.status, 'assistindo')

    def test_titulo_do_tmdb_so_altera_status(self):
        importado = Titulo.objects.create(nome='Duna', tipo='filme', genero=self.genero, tmdb_id=438631)
        item = ItemBiblioteca.objects.create(usuario=self.usuario, titulo=importado)
        self.client.post(reverse('editar_item', args=[item.id]), {'nome': 'Outro nome', 'status': 'assistido'})
        importado.refresh_from_db()
        item.refresh_from_db()
        self.assertEqual(importado.nome, 'Duna')
        self.assertEqual(item.status, 'assistido')

    def test_nao_acessa_item_de_outro_usuario(self):
        item_outro = ItemBiblioteca.objects.create(
            usuario=self.outro, titulo=Titulo.objects.create(nome='Aquarius', tipo='filme', genero=self.genero))
        self.assertEqual(self.client.get(reverse('detalhe_item', args=[item_outro.id])).status_code, 404)
        self.assertEqual(self.client.post(reverse('excluir_item', args=[item_outro.id])).status_code, 404)

    def test_excluir_item_remove_avaliacao(self):
        Avaliacao.objects.create(item_biblioteca=self.item, nota=9)
        resposta = self.client.post(reverse('excluir_item', args=[self.item.id]))
        self.assertRedirects(resposta, reverse('lista_biblioteca'))
        self.assertFalse(ItemBiblioteca.objects.filter(id=self.item.id).exists())
        self.assertFalse(Avaliacao.objects.exists())
        # UC07: o título permanece no catálogo
        self.assertTrue(Titulo.objects.filter(id=self.titulo.id).exists())
