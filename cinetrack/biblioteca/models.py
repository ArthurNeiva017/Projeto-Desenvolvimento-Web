"""
Models do CineTrack, conforme o Modelo Lógico do Banco de Dados
(docs/modelagem/banco-de-dados).

O usuário é o model User do próprio Django (django.contrib.auth), que já
armazena a senha com hash.
"""
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Genero(models.Model):
    nome = models.CharField(max_length=60, unique=True, verbose_name='Nome')
    tmdb_id = models.IntegerField(unique=True, null=True, blank=True, verbose_name='ID no TMDB')

    class Meta:
        db_table = 'genero'
        ordering = ['nome']
        verbose_name = 'Gênero'
        verbose_name_plural = 'Gêneros'

    def __str__(self):
        return self.nome


class Titulo(models.Model):
    TIPO_FILME = 'filme'
    TIPO_SERIE = 'serie'
    TIPO_CHOICES = [
        (TIPO_FILME, 'Filme'),
        (TIPO_SERIE, 'Série'),
    ]

    # Filmes e séries do TMDB podem ter o mesmo ID; por isso a unicidade é (tmdb_id, tipo)
    tmdb_id = models.IntegerField(null=True, blank=True, verbose_name='ID no TMDB')
    genero = models.ForeignKey(Genero, on_delete=models.PROTECT, related_name='titulos', verbose_name='Gênero')
    nome = models.CharField(max_length=200, verbose_name='Título')
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, verbose_name='Tipo')
    sinopse = models.TextField(blank=True, verbose_name='Sinopse')
    ano_lancamento = models.PositiveIntegerField(null=True, blank=True, verbose_name='Ano de lançamento')
    poster_url = models.URLField(max_length=255, blank=True, verbose_name='URL do pôster')

    class Meta:
        db_table = 'titulo'
        ordering = ['nome']
        verbose_name = 'Título'
        verbose_name_plural = 'Títulos'
        constraints = [
            models.UniqueConstraint(fields=['tmdb_id', 'tipo'], name='titulo_tmdb_unico'),
        ]

    def __str__(self):
        if self.ano_lancamento:
            return f'{self.nome} ({self.ano_lancamento})'
        return self.nome

    @property
    def importado_tmdb(self):
        return self.tmdb_id is not None


class ItemBiblioteca(models.Model):
    STATUS_QUERO = 'quero_assistir'
    STATUS_ASSISTINDO = 'assistindo'
    STATUS_ASSISTIDO = 'assistido'
    STATUS_CHOICES = [
        (STATUS_QUERO, 'Quero assistir'),
        (STATUS_ASSISTINDO, 'Assistindo'),
        (STATUS_ASSISTIDO, 'Assistido'),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='itens_biblioteca', verbose_name='Usuário',
    )
    titulo = models.ForeignKey(Titulo, on_delete=models.PROTECT, related_name='itens', verbose_name='Título')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_QUERO, verbose_name='Status')
    adicionado_em = models.DateTimeField(auto_now_add=True, verbose_name='Adicionado em')
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')

    class Meta:
        db_table = 'item_biblioteca'
        ordering = ['-atualizado_em']
        verbose_name = 'Item da biblioteca'
        verbose_name_plural = 'Itens da biblioteca'
        constraints = [
            # Um usuário não pode ter o mesmo título duas vezes na biblioteca
            models.UniqueConstraint(fields=['usuario', 'titulo'], name='item_usuario_titulo_unico'),
        ]

    def __str__(self):
        return f'{self.titulo} - {self.get_status_display()} ({self.usuario})'


class Avaliacao(models.Model):
    # Cada item da biblioteca tem no máximo uma avaliação (1 para 0..1)
    item_biblioteca = models.OneToOneField(
        ItemBiblioteca, on_delete=models.CASCADE, related_name='avaliacao', verbose_name='Item da biblioteca',
    )
    nota = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(10)], verbose_name='Nota (0 a 10)',
    )
    comentario = models.CharField(max_length=255, blank=True, verbose_name='Comentário')
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')

    class Meta:
        db_table = 'avaliacao'
        ordering = ['-criado_em']
        verbose_name = 'Avaliação'
        verbose_name_plural = 'Avaliações'

    def __str__(self):
        return f'{self.item_biblioteca.titulo} - nota {self.nota}'
