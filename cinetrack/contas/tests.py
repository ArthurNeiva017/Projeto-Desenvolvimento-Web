# Testes automatizados do app contas (cadastro, login e logout).
# Executar com: python manage.py test
# Cada método que começa com "test_" é um caso de teste. O Django cria um banco
# de dados temporário só para os testes, que é apagado no final.
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class ContasTests(TestCase):
    # Teste: A página inicial abre (status 200) e mostra o nome do sistema
    def test_pagina_inicial_abre(self):
        resposta = self.client.get(reverse('index'))
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, 'CineTrack')

    # Teste: Cadastro válido cria o usuário e redireciona para o login
    def test_registro_cria_usuario(self):
        resposta = self.client.post(reverse('register'), {
            'username': 'maria',
            'email': 'maria@exemplo.com',
            'password': 'SenhaForte#2026',
            'confirm_password': 'SenhaForte#2026',
        })
        self.assertRedirects(resposta, reverse('login'))
        self.assertTrue(User.objects.filter(username='maria').exists())

    # Teste: Senha e confirmação diferentes: o usuário NÃO é criado
    def test_registro_senhas_diferentes(self):
        resposta = self.client.post(reverse('register'), {
            'username': 'joao',
            'password': 'SenhaForte#2026',
            'confirm_password': 'outra',
        })
        self.assertEqual(resposta.status_code, 200)
        self.assertFalse(User.objects.filter(username='joao').exists())

    # Teste: Login correto leva ao dashboard; logout leva de volta ao login
    def test_login_e_logout(self):
        User.objects.create_user(username='ana', password='SenhaForte#2026')
        resposta = self.client.post(reverse('login'), {'username': 'ana', 'password': 'SenhaForte#2026'})
        self.assertRedirects(resposta, reverse('dashboard'))
        resposta = self.client.post(reverse('logout'))
        self.assertRedirects(resposta, reverse('login'))

    # Teste: Usuário/senha errados mostram mensagem de erro
    def test_login_invalido(self):
        resposta = self.client.post(reverse('login'), {'username': 'x', 'password': 'y'})
        self.assertContains(resposta, 'Usuário ou senha inválidos')

    # Teste: Logout por GET é recusado (405 = método não permitido)
    def test_logout_por_get_nao_permitido(self):
        resposta = self.client.get(reverse('logout'))
        self.assertEqual(resposta.status_code, 405)
