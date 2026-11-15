# Rotas do app avaliacoes (prefixo "avaliacoes/" definido no urls.py do projeto)
from django.urls import path
from . import views

urlpatterns = [
    # /avaliacoes/5/  → avaliar (ou alterar a avaliação de) o item 5 da biblioteca
    path('<int:id>/', views.avaliar_item, name='avaliar_item'),
    # /avaliacoes/5/excluir/  → remover a avaliação do item 5
    path('<int:id>/excluir/', views.excluir_avaliacao, name='excluir_avaliacao'),
]
