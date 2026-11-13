from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class ContasTests(TestCase):
    def test_pagina_inicial_abre(self):
        resposta = self.client.get(reverse('index'))
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, 'CineTrack')

    def test_registro_cria_usuario(self):
        resposta = self.client.post(reverse('register'), {
            'username': 'maria',
            'email': 'maria@exemplo.com',
            'password': 'SenhaForte#2026',
            'confirm_password': 'SenhaForte#2026',
        })
        self.assertRedirects(resposta, reverse('login'))
        self.assertTrue(User.objects.filter(username='maria').exists())

    def test_registro_senhas_diferentes(self):
        resposta = self.client.post(reverse('register'), {
            'username': 'joao',
            'password': 'SenhaForte#2026',
            'confirm_password': 'outra',
        })
        self.assertEqual(resposta.status_code, 200)
        self.assertFalse(User.objects.filter(username='joao').exists())

    def test_login_e_logout(self):
        User.objects.create_user(username='ana', password='SenhaForte#2026')
        resposta = self.client.post(reverse('login'), {'username': 'ana', 'password': 'SenhaForte#2026'})
        self.assertRedirects(resposta, reverse('dashboard'))
        resposta = self.client.post(reverse('logout'))
        self.assertRedirects(resposta, reverse('login'))

    def test_login_invalido(self):
        resposta = self.client.post(reverse('login'), {'username': 'x', 'password': 'y'})
        self.assertContains(resposta, 'Usuário ou senha inválidos')

    def test_logout_por_get_nao_permitido(self):
        resposta = self.client.get(reverse('logout'))
        self.assertEqual(resposta.status_code, 405)
