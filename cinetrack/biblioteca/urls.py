# Rotas (URLs) do app biblioteca.
# Este arquivo é incluído no urls.py do projeto com o prefixo "biblioteca/".
from django.urls import path
from . import views

# Cada path liga um endereço a uma view. O "name" permite referenciar a rota
# pelo nome (ex.: redirect('lista_biblioteca') ou {% url 'lista_biblioteca' %}),
# sem escrever o endereço fixo no código.
urlpatterns = [
    path('', views.lista_biblioteca, name='lista_biblioteca'),          # /biblioteca/
    path('novo/', views.criar_item, name='criar_item'),                 # /biblioteca/novo/
    # <int:id> captura um número da URL e o envia para a view no parâmetro "id"
    path('<int:id>/', views.detalhe_item, name='detalhe_item'),         # /biblioteca/5/
    path('<int:id>/editar/', views.editar_item, name='editar_item'),    # /biblioteca/5/editar/
    path('<int:id>/excluir/', views.excluir_item, name='excluir_item'), # /biblioteca/5/excluir/
]
