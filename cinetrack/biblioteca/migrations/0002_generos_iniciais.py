"""
Migration de dados: cadastra os gêneros iniciais com os IDs usados pelo TMDB,
para que a importação de títulos consiga associar o gênero correto.
"""
from django.db import migrations

GENEROS = [
    ('Ação', 28), ('Aventura', 12), ('Animação', 16), ('Comédia', 35), ('Crime', 80),
    ('Documentário', 99), ('Drama', 18), ('Família', 10751), ('Fantasia', 14),
    ('História', 36), ('Terror', 27), ('Música', 10402), ('Mistério', 9648),
    ('Romance', 10749), ('Ficção científica', 878), ('Cinema TV', 10770),
    ('Thriller', 53), ('Guerra', 10752), ('Faroeste', 37),
    ('Ação e Aventura', 10759), ('Kids', 10762), ('Reality', 10764),
    ('Ficção científica e Fantasia', 10765), ('Guerra e Política', 10768),
    ('Outros', None),
]


def criar_generos(apps, schema_editor):
    Genero = apps.get_model('biblioteca', 'Genero')
    for nome, tmdb_id in GENEROS:
        Genero.objects.get_or_create(nome=nome, defaults={'tmdb_id': tmdb_id})


def remover_generos(apps, schema_editor):
    Genero = apps.get_model('biblioteca', 'Genero')
    Genero.objects.filter(nome__in=[nome for nome, _ in GENEROS], titulos__isnull=True).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('biblioteca', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(criar_generos, remover_generos),
    ]
