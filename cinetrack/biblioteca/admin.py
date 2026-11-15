# Configuração do painel administrativo do Django (/admin/).
# Registrar um model aqui faz ele aparecer no painel, com telas prontas de
# listar, criar, editar e excluir registros.
from django.contrib import admin

from .models import Avaliacao, Genero, ItemBiblioteca, Titulo


# @admin.register(Model) registra o model no admin usando as opções da classe abaixo
@admin.register(Genero)
class GeneroAdmin(admin.ModelAdmin):
    list_display = ['nome', 'tmdb_id']  # colunas exibidas na listagem
    search_fields = ['nome']            # campos usados pela caixa de pesquisa


@admin.register(Titulo)
class TituloAdmin(admin.ModelAdmin):
    list_display = ['nome', 'tipo', 'genero', 'ano_lancamento', 'tmdb_id']
    list_filter = ['tipo', 'genero']    # filtros exibidos na barra lateral
    search_fields = ['nome']


@admin.register(ItemBiblioteca)
class ItemBibliotecaAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'usuario', 'status', 'atualizado_em']
    # "titulo__tipo" filtra pelo campo "tipo" do título relacionado
    list_filter = ['status', 'titulo__tipo']
    search_fields = ['titulo__nome', 'usuario__username']


@admin.register(Avaliacao)
class AvaliacaoAdmin(admin.ModelAdmin):
    list_display = ['item_biblioteca', 'nota', 'criado_em']
    list_filter = ['nota']
