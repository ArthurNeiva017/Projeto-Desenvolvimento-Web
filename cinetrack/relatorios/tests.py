# Testes automatizados do app relatorios (dashboard, relatório e CSV).
# Executar com: python manage.py test
# Cada método que começa com "test_" é um caso de teste. O Django cria um banco
# de dados temporário só para os testes, que é apagado no final.
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from biblioteca.models import Avaliacao, Genero, ItemBiblioteca, Titulo


class RelatoriosTests(TestCase):
    # setUp roda ANTES de cada teste: prepara os dados necessários
    def setUp(self):
        self.usuario = User.objects.create_user(username='ana', password='SenhaForte#2026')
        drama = Genero.objects.get(nome='Drama')
        t1 = Titulo.objects.create(nome='Bacurau', tipo='filme', genero=drama)
        t2 = Titulo.objects.create(nome='=CMD()', tipo='serie', genero=drama)
        i1 = ItemBiblioteca.objects.create(usuario=self.usuario, titulo=t1, status='assistido')
        ItemBiblioteca.objects.create(usuario=self.usuario, titulo=t2, status='quero_assistir')
        Avaliacao.objects.create(item_biblioteca=i1, nota=9)
        self.client.login(username='ana', password='SenhaForte#2026')

    # Teste: O dashboard calcula corretamente o total de itens e a nota média
    def test_dashboard_indicadores(self):
        resposta = self.client.get(reverse('dashboard'))
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.context['ind']['total'], 2)
        self.assertEqual(resposta.context['ind']['nota_media'], 9)

    # Teste: O relatório aplica o filtro de status
    def test_relatorio_filtra_por_status(self):
        resposta = self.client.get(reverse('relatorio'), {'status': 'assistido'})
        self.assertEqual(resposta.context['ind']['total'], 1)
        self.assertContains(resposta, 'Bacurau')

    # Teste: Data inicial maior que a final mostra mensagem de erro
    def test_relatorio_datas_invalidas(self):
        resposta = self.client.get(reverse('relatorio'), {'data_inicio': '2026-12-01', 'data_fim': '2026-01-01'})
        self.assertContains(resposta, 'data inicial deve ser anterior')

    # Teste: A exportação gera um CSV e protege contra injeção de fórmulas no Excel
    def test_exportar_csv(self):
        resposta = self.client.get(reverse('relatorio_csv'))
        self.assertEqual(resposta['Content-Type'], 'text/csv; charset=utf-8')
        conteudo = resposta.content.decode('utf-8-sig')
        self.assertIn('Bacurau', conteudo)
        # proteção contra injeção de fórmula no Excel
        self.assertIn("'=CMD()", conteudo)

    # Teste: Sem login, o relatório redireciona para o login
    def test_relatorio_exige_login(self):
        self.client.logout()
        self.assertEqual(self.client.get(reverse('relatorio')).status_code, 302)
