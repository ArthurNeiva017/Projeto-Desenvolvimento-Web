# Testes automatizados da API REST (catálogo público e biblioteca com JWT).
# Executar com: python manage.py test
# Cada método que começa com "test_" é um caso de teste. O Django cria um banco
# de dados temporário só para os testes, que é apagado no final.
from django.contrib.auth.models import User
from django.core.cache import cache
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from biblioteca.models import Avaliacao, Genero, ItemBiblioteca, Titulo


class APITests(APITestCase):
    # setUp roda ANTES de cada teste: prepara os dados necessários
    def setUp(self):
        cache.clear()  # zera os contadores de throttling
        self.usuario = User.objects.create_user(username='ana', password='SenhaForte#2026')
        self.outro = User.objects.create_user(username='bia', password='SenhaForte#2026')
        self.drama = Genero.objects.get(nome='Drama')
        self.filme = Titulo.objects.create(nome='Bacurau', tipo='filme', genero=self.drama, ano_lancamento=2019)
        self.serie = Titulo.objects.create(nome='Sintonia', tipo='serie', genero=self.drama, ano_lancamento=2019)

    # Função auxiliar: pede um token JWT e passa a enviá-lo nas próximas requisições
    def autenticar(self, username='ana'):
        resposta = self.client.post(reverse('token_obtain_pair'), {'username': username, 'password': 'SenhaForte#2026'}, format='json')
        self.assertEqual(resposta.status_code, status.HTTP_200_OK)
        self.assertIn('refresh', resposta.data)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {resposta.data["access"]}')

    # --- Catálogo público ---
    # Teste: O catálogo é público e a resposta vem paginada (count/results)
    def test_lista_titulos_publica_com_paginacao(self):
        resposta = self.client.get('/api/v1/titulos/')
        self.assertEqual(resposta.status_code, status.HTTP_200_OK)
        self.assertEqual(resposta.data['count'], 2)
        self.assertIn('results', resposta.data)

    # Teste: Os filtros ?tipo= e ?busca= da API funcionam
    def test_filtros_de_titulos(self):
        resposta = self.client.get('/api/v1/titulos/', {'tipo': 'serie'})
        self.assertEqual([t['nome'] for t in resposta.data['results']], ['Sintonia'])
        resposta = self.client.get('/api/v1/titulos/', {'busca': 'bacu'})
        self.assertEqual([t['nome'] for t in resposta.data['results']], ['Bacurau'])

    # Teste: Título inexistente retorna 404
    def test_titulo_inexistente_retorna_404(self):
        self.assertEqual(self.client.get('/api/v1/titulos/99999/').status_code, status.HTTP_404_NOT_FOUND)

    # Teste: O catálogo é somente leitura: POST retorna 405
    def test_catalogo_e_somente_leitura(self):
        self.autenticar()
        resposta = self.client.post('/api/v1/titulos/', {'nome': 'X'}, format='json')
        self.assertEqual(resposta.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    # --- Biblioteca protegida por JWT ---
    # Teste: A biblioteca exige token: sem ele retorna 401
    def test_biblioteca_sem_token_retorna_401(self):
        resposta = self.client.get('/api/v1/biblioteca/')
        self.assertEqual(resposta.status_code, status.HTTP_401_UNAUTHORIZED)

    # Teste: Fluxo completo de CRUD pela API: criar, listar, alterar e excluir
    def test_crud_da_biblioteca(self):
        self.autenticar()
        # CREATE
        resposta = self.client.post('/api/v1/biblioteca/', {'titulo_id': self.filme.id, 'status': 'assistindo'}, format='json')
        self.assertEqual(resposta.status_code, status.HTTP_201_CREATED)
        item_id = resposta.data['id']
        self.assertEqual(resposta.data['titulo']['nome'], 'Bacurau')
        # LIST
        resposta = self.client.get('/api/v1/biblioteca/')
        self.assertEqual(resposta.data['count'], 1)
        # PATCH
        resposta = self.client.patch(f'/api/v1/biblioteca/{item_id}/', {'status': 'assistido'}, format='json')
        self.assertEqual(resposta.status_code, status.HTTP_200_OK)
        self.assertEqual(resposta.data['status'], 'assistido')
        # DELETE
        resposta = self.client.delete(f'/api/v1/biblioteca/{item_id}/')
        self.assertEqual(resposta.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(ItemBiblioteca.objects.exists())

    # Teste: Adicionar o mesmo título duas vezes retorna 400
    def test_titulo_duplicado_retorna_400(self):
        self.autenticar()
        ItemBiblioteca.objects.create(usuario=self.usuario, titulo=self.filme)
        resposta = self.client.post('/api/v1/biblioteca/', {'titulo_id': self.filme.id}, format='json')
        self.assertEqual(resposta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('titulo_id', resposta.data)

    # Teste: Status inválido retorna 400
    def test_status_invalido_retorna_400(self):
        self.autenticar()
        resposta = self.client.post('/api/v1/biblioteca/', {'titulo_id': self.filme.id, 'status': 'xyz'}, format='json')
        self.assertEqual(resposta.status_code, status.HTTP_400_BAD_REQUEST)

    # Teste: Acessar/excluir item de outro usuário retorna 404
    def test_nao_acessa_item_de_outro_usuario(self):
        item_outro = ItemBiblioteca.objects.create(usuario=self.outro, titulo=self.filme)
        self.autenticar()
        self.assertEqual(self.client.get(f'/api/v1/biblioteca/{item_outro.id}/').status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(self.client.delete(f'/api/v1/biblioteca/{item_outro.id}/').status_code, status.HTTP_404_NOT_FOUND)

    # Teste: Avaliar pela API: 201 ao criar, 200 ao alterar, 400 com nota inválida
    def test_avaliar_item(self):
        item = ItemBiblioteca.objects.create(usuario=self.usuario, titulo=self.filme)
        self.autenticar()
        url = f'/api/v1/biblioteca/{item.id}/avaliar/'
        resposta = self.client.post(url, {'nota': 9, 'comentario': 'Ótimo'}, format='json')
        self.assertEqual(resposta.status_code, status.HTTP_201_CREATED)
        resposta = self.client.post(url, {'nota': 10}, format='json')
        self.assertEqual(resposta.status_code, status.HTTP_200_OK)
        self.assertEqual(Avaliacao.objects.get().nota, 10)
        resposta = self.client.post(url, {'nota': 11}, format='json')
        self.assertEqual(resposta.status_code, status.HTTP_400_BAD_REQUEST)

    # Teste: O endpoint de relatório devolve os totais corretos
    def test_relatorio(self):
        ItemBiblioteca.objects.create(usuario=self.usuario, titulo=self.filme, status='assistido')
        ItemBiblioteca.objects.create(usuario=self.usuario, titulo=self.serie)
        self.autenticar()
        resposta = self.client.get('/api/v1/biblioteca/relatorio/')
        self.assertEqual(resposta.status_code, status.HTTP_200_OK)
        self.assertEqual(resposta.data['total'], 2)
        self.assertEqual(resposta.data['por_status']['assistido'], 1)
        self.assertEqual(resposta.data['por_tipo'], {'filme': 1, 'serie': 1})

    # Teste: Pedir token com senha errada retorna 401
    def test_token_com_senha_errada(self):
        resposta = self.client.post(reverse('token_obtain_pair'), {'username': 'ana', 'password': 'errada'}, format='json')
        self.assertEqual(resposta.status_code, status.HTTP_401_UNAUTHORIZED)

    # Teste: A documentação Swagger e o esquema OpenAPI estão acessíveis
    def test_documentacao_swagger_disponivel(self):
        self.assertEqual(self.client.get(reverse('swagger-ui')).status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.get(reverse('schema')).status_code, status.HTTP_200_OK)
