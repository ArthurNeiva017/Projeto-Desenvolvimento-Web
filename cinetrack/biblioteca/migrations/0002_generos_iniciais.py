"""
Migration de dados: cadastra os gêneros iniciais com os IDs usados pelo TMDB,
para que a importação de títulos consiga associar o gênero correto.
"""
from django.db import migrations

# Lista de pares (nome do gênero, ID do gênero no TMDB)
GENEROS = [
    ('Ação', 28), ('Aventura', 12), ('Animação', 16), ('Comédia', 35), ('Crime', 80),
    ('Documentário', 99), ('Drama', 18), ('Família', 10751), ('Fantasia', 14),
    ('História', 36), ('Terror', 27), ('Música', 10402), ('Mistério', 9648),
    ('Romance', 10749), ('Ficção científica', 878), ('Cinema TV', 10770),
    ('Thriller', 53), ('Guerra', 10752), ('Faroeste', 37),
    ('Ação e Aventura', 10759), ('Kids', 10762), ('Reality', 10764),
    ('Ficção científica e Fantasia', 10765), ('Guerra e Política', 10768),
    ('Outros', None),  # gênero genérico, usado quando o TMDB não informa o gênero
]


# Executada ao rodar "python manage.py migrate": insere os gêneros no banco
def criar_generos(apps, schema_editor):
    # Em migrations, o model é obtido por apps.get_model (versão do model naquele momento da história)
    Genero = apps.get_model('biblioteca', 'Genero')
    for nome, tmdb_id in GENEROS:
        # get_or_create evita duplicar caso o gênero já exista
        Genero.objects.get_or_create(nome=nome, defaults={'tmdb_id': tmdb_id})


# Executada ao DESFAZER a migration: remove os gêneros que não estão em uso por nenhum título
def remover_generos(apps, schema_editor):
    Genero = apps.get_model('biblioteca', 'Genero')
    Genero.objects.filter(nome__in=[nome for nome, _ in GENEROS], titulos__isnull=True).delete()


class Migration(migrations.Migration):

    # Esta migration só roda depois da 0001 (que cria as tabelas)
    dependencies = [
        ('biblioteca', '0001_initial'),
    ]

    # RunPython executa código Python: (função para aplicar, função para desfazer)
    operations = [
        migrations.RunPython(criar_generos, remover_generos),
    ]
