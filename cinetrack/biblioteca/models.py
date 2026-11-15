"""
Models do CineTrack, conforme o Modelo Lógico do Banco de Dados
(docs/modelagem/banco-de-dados).

O usuário é o model User do próprio Django (django.contrib.auth), que já
armazena a senha com hash.
"""
# "settings" dá acesso às configurações do projeto (usamos AUTH_USER_MODEL)
from django.conf import settings
# Validadores prontos do Django para limitar valores numéricos (nota de 0 a 10)
from django.core.validators import MaxValueValidator, MinValueValidator
# "models" contém as classes base para criar tabelas (Model) e os tipos de campo
from django.db import models


# ---------------------------------------------------------------------------
# GÊNERO
# Cada classe que herda de models.Model vira uma tabela no banco de dados.
# Cada atributo (CharField, IntegerField...) vira uma coluna dessa tabela.
# ---------------------------------------------------------------------------
class Genero(models.Model):
    # Nome do gênero (ex.: "Ação"). unique=True impede gêneros repetidos
    nome = models.CharField(max_length=60, unique=True, verbose_name='Nome')
    # ID do gênero na API do TMDB. null/blank=True: é opcional (gêneros criados à mão não têm)
    tmdb_id = models.IntegerField(unique=True, null=True, blank=True, verbose_name='ID no TMDB')

    # A classe Meta guarda configurações extras do model (não são colunas)
    class Meta:
        db_table = 'genero'            # nome real da tabela no banco
        ordering = ['nome']            # consultas vêm ordenadas por nome (A→Z)
        verbose_name = 'Gênero'        # nome exibido no painel admin (singular)
        verbose_name_plural = 'Gêneros'  # nome exibido no painel admin (plural)

    # __str__ define como o objeto aparece como texto (ex.: em selects e no admin)
    def __str__(self):
        return self.nome


# ---------------------------------------------------------------------------
# TÍTULO (filme ou série)
# Representa o "catálogo": os dados do filme/série, independentes do usuário.
# ---------------------------------------------------------------------------
class Titulo(models.Model):
    # Constantes para os tipos possíveis, evitando escrever as strings "soltas" no código
    TIPO_FILME = 'filme'
    TIPO_SERIE = 'serie'
    # Lista de opções: (valor salvo no banco, texto mostrado na tela)
    TIPO_CHOICES = [
        (TIPO_FILME, 'Filme'),
        (TIPO_SERIE, 'Série'),
    ]

    # Filmes e séries do TMDB podem ter o mesmo ID; por isso a unicidade é (tmdb_id, tipo)
    tmdb_id = models.IntegerField(null=True, blank=True, verbose_name='ID no TMDB')
    # Chave estrangeira (relacionamento N:1): muitos títulos pertencem a um gênero.
    # on_delete=PROTECT impede apagar um gênero que ainda tenha títulos ligados a ele.
    # related_name='titulos' permite fazer genero.titulos.all()
    genero = models.ForeignKey(Genero, on_delete=models.PROTECT, related_name='titulos', verbose_name='Gênero')
    nome = models.CharField(max_length=200, verbose_name='Título')
    # choices=TIPO_CHOICES faz o campo aceitar apenas "filme" ou "serie"
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, verbose_name='Tipo')
    # TextField = texto longo, sem limite de tamanho. blank=True: pode ficar vazio
    sinopse = models.TextField(blank=True, verbose_name='Sinopse')
    # PositiveIntegerField só aceita números >= 0
    ano_lancamento = models.PositiveIntegerField(null=True, blank=True, verbose_name='Ano de lançamento')
    # URLField valida automaticamente se o texto é um endereço web válido
    poster_url = models.URLField(max_length=255, blank=True, verbose_name='URL do pôster')

    class Meta:
        db_table = 'titulo'
        ordering = ['nome']
        verbose_name = 'Título'
        verbose_name_plural = 'Títulos'
        # Restrição no banco: não pode existir dois títulos com o mesmo par (tmdb_id, tipo)
        constraints = [
            models.UniqueConstraint(fields=['tmdb_id', 'tipo'], name='titulo_tmdb_unico'),
        ]

    def __str__(self):
        # Mostra "Nome (Ano)" quando o ano é conhecido, senão apenas o nome
        if self.ano_lancamento:
            return f'{self.nome} ({self.ano_lancamento})'
        return self.nome

    # @property permite acessar como atributo: titulo.importado_tmdb (sem parênteses)
    @property
    def importado_tmdb(self):
        # Se o título tem tmdb_id, ele veio da API do TMDB; se não, foi cadastrado manualmente
        return self.tmdb_id is not None


# ---------------------------------------------------------------------------
# ITEM DA BIBLIOTECA
# Liga um USUÁRIO a um TÍTULO e guarda o status (quero assistir/assistindo/assistido).
# É a "biblioteca pessoal" de cada usuário.
# ---------------------------------------------------------------------------
class ItemBiblioteca(models.Model):
    # Constantes dos status possíveis
    STATUS_QUERO = 'quero_assistir'
    STATUS_ASSISTINDO = 'assistindo'
    STATUS_ASSISTIDO = 'assistido'
    STATUS_CHOICES = [
        (STATUS_QUERO, 'Quero assistir'),
        (STATUS_ASSISTINDO, 'Assistindo'),
        (STATUS_ASSISTIDO, 'Assistido'),
    ]

    # Dono do item. settings.AUTH_USER_MODEL aponta para o model User do Django.
    # on_delete=CASCADE: se o usuário for apagado, os itens dele também são.
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='itens_biblioteca', verbose_name='Usuário',
    )
    # Título associado. PROTECT: não deixa apagar um título que esteja em alguma biblioteca
    titulo = models.ForeignKey(Titulo, on_delete=models.PROTECT, related_name='itens', verbose_name='Título')
    # Status atual; por padrão (default) começa como "Quero assistir"
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_QUERO, verbose_name='Status')
    # auto_now_add=True: data/hora preenchida automaticamente só na criação
    adicionado_em = models.DateTimeField(auto_now_add=True, verbose_name='Adicionado em')
    # auto_now=True: data/hora atualizada automaticamente a cada vez que o item é salvo
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')

    class Meta:
        db_table = 'item_biblioteca'
        ordering = ['-atualizado_em']  # o "-" indica ordem decrescente (mais recentes primeiro)
        verbose_name = 'Item da biblioteca'
        verbose_name_plural = 'Itens da biblioteca'
        constraints = [
            # Um usuário não pode ter o mesmo título duas vezes na biblioteca
            models.UniqueConstraint(fields=['usuario', 'titulo'], name='item_usuario_titulo_unico'),
        ]

    def __str__(self):
        # get_status_display() é criado pelo Django e devolve o texto amigável do status
        return f'{self.titulo} - {self.get_status_display()} ({self.usuario})'


# ---------------------------------------------------------------------------
# AVALIAÇÃO
# Nota (0 a 10) e comentário que o usuário dá para um item da sua biblioteca.
# ---------------------------------------------------------------------------
class Avaliacao(models.Model):
    # Cada item da biblioteca tem no máximo uma avaliação (1 para 0..1)
    # OneToOneField = relacionamento 1:1. Com related_name='avaliacao' acessamos item.avaliacao
    item_biblioteca = models.OneToOneField(
        ItemBiblioteca, on_delete=models.CASCADE, related_name='avaliacao', verbose_name='Item da biblioteca',
    )
    # Nota inteira pequena, validada para ficar entre 0 e 10
    nota = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(10)], verbose_name='Nota (0 a 10)',
    )
    # Comentário opcional de até 255 caracteres
    comentario = models.CharField(max_length=255, blank=True, verbose_name='Comentário')
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')

    class Meta:
        db_table = 'avaliacao'
        ordering = ['-criado_em']  # avaliações mais recentes primeiro
        verbose_name = 'Avaliação'
        verbose_name_plural = 'Avaliações'

    def __str__(self):
        return f'{self.item_biblioteca.titulo} - nota {self.nota}'
