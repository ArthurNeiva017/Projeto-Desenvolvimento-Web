from django.contrib import admin

from .models import Avaliacao, Genero, ItemBiblioteca, Titulo


@admin.register(Genero)
class GeneroAdmin(admin.ModelAdmin):
    list_display = ['nome', 'tmdb_id']
    search_fields = ['nome']


@admin.register(Titulo)
class TituloAdmin(admin.ModelAdmin):
    list_display = ['nome', 'tipo', 'genero', 'ano_lancamento', 'tmdb_id']
    list_filter = ['tipo', 'genero']
    search_fields = ['nome']


@admin.register(ItemBiblioteca)
class ItemBibliotecaAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'usuario', 'status', 'atualizado_em']
    list_filter = ['status', 'titulo__tipo']
    search_fields = ['titulo__nome', 'usuario__username']


@admin.register(Avaliacao)
class AvaliacaoAdmin(admin.ModelAdmin):
    list_display = ['item_biblioteca', 'nota', 'criado_em']
    list_filter = ['nota']
