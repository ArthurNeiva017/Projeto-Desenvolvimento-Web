from django.urls import path
from . import views

urlpatterns = [
    path('<int:id>/', views.avaliar_item, name='avaliar_item'),
    path('<int:id>/excluir/', views.excluir_avaliacao, name='excluir_avaliacao'),
]
