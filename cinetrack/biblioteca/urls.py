from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_biblioteca, name='lista_biblioteca'),
    path('novo/', views.criar_item, name='criar_item'),
    path('<int:id>/', views.detalhe_item, name='detalhe_item'),
    path('<int:id>/editar/', views.editar_item, name='editar_item'),
    path('<int:id>/excluir/', views.excluir_item, name='excluir_item'),
]
