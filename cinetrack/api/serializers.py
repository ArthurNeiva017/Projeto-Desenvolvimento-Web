"""
Serializers da API REST: convertem os objetos do banco para JSON e vice-versa.
"""
from rest_framework import serializers

from biblioteca.models import Avaliacao, Genero, ItemBiblioteca, Titulo


class GeneroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genero
        fields = ['id', 'nome', 'tmdb_id']


class TituloSerializer(serializers.ModelSerializer):
    genero = GeneroSerializer(read_only=True)

    class Meta:
        model = Titulo
        fields = ['id', 'nome', 'tipo', 'genero', 'ano_lancamento', 'sinopse', 'poster_url', 'tmdb_id']


class AvaliacaoSerializer(serializers.ModelSerializer):
    nota = serializers.IntegerField(min_value=0, max_value=10)

    class Meta:
        model = Avaliacao
        fields = ['nota', 'comentario', 'criado_em']
        read_only_fields = ['criado_em']


class ItemBibliotecaSerializer(serializers.ModelSerializer):
    titulo = TituloSerializer(read_only=True)
    titulo_id = serializers.PrimaryKeyRelatedField(
        queryset=Titulo.objects.all(), source='titulo', write_only=True,
        help_text='ID do título no catálogo (GET /api/v1/titulos/).',
    )
    avaliacao = serializers.SerializerMethodField()

    class Meta:
        model = ItemBiblioteca
        fields = ['id', 'titulo', 'titulo_id', 'status', 'avaliacao', 'adicionado_em', 'atualizado_em']
        read_only_fields = ['adicionado_em', 'atualizado_em']

    def get_avaliacao(self, item) -> dict | None:
        avaliacao = getattr(item, 'avaliacao', None)
        return AvaliacaoSerializer(avaliacao).data if avaliacao else None

    def validate(self, attrs):
        usuario = self.context['request'].user
        titulo = attrs.get('titulo')
        if self.instance is None:
            # Um usuário não pode ter o mesmo título duas vezes na biblioteca
            if ItemBiblioteca.objects.filter(usuario=usuario, titulo=titulo).exists():
                raise serializers.ValidationError({'titulo_id': 'Este título já está na sua biblioteca.'})
        elif titulo is not None and titulo != self.instance.titulo:
            raise serializers.ValidationError({'titulo_id': 'Não é possível trocar o título de um item; altere apenas o status.'})
        return attrs
