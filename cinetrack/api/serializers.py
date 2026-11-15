"""
Serializers da API REST: convertem os objetos do banco para JSON e vice-versa.
"""
from rest_framework import serializers

from biblioteca.models import Avaliacao, Genero, ItemBiblioteca, Titulo


# ModelSerializer: gera automaticamente a conversão a partir do model,
# de forma parecida com o ModelForm dos formulários HTML
class GeneroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genero
        fields = ['id', 'nome', 'tmdb_id']  # campos que aparecem no JSON


class TituloSerializer(serializers.ModelSerializer):
    # Em vez de mostrar só o id do gênero, mostra o objeto gênero completo (serializer aninhado)
    genero = GeneroSerializer(read_only=True)

    class Meta:
        model = Titulo
        fields = ['id', 'nome', 'tipo', 'genero', 'ano_lancamento', 'sinopse', 'poster_url', 'tmdb_id']


class AvaliacaoSerializer(serializers.ModelSerializer):
    # Redefine o campo nota para validar o intervalo 0 a 10 também na API
    nota = serializers.IntegerField(min_value=0, max_value=10)

    class Meta:
        model = Avaliacao
        fields = ['nota', 'comentario', 'criado_em']
        read_only_fields = ['criado_em']  # aparece na resposta, mas não pode ser enviado pelo cliente


class ItemBibliotecaSerializer(serializers.ModelSerializer):
    # Na LEITURA (GET), o título aparece completo
    titulo = TituloSerializer(read_only=True)
    # Na ESCRITA (POST), o cliente envia apenas o id do título em "titulo_id".
    # source='titulo' indica que esse valor preenche o campo "titulo" do model
    titulo_id = serializers.PrimaryKeyRelatedField(
        queryset=Titulo.objects.all(), source='titulo', write_only=True,
        help_text='ID do título no catálogo (GET /api/v1/titulos/).',
    )
    # Campo calculado: o valor vem do método get_avaliacao abaixo
    avaliacao = serializers.SerializerMethodField()

    class Meta:
        model = ItemBiblioteca
        fields = ['id', 'titulo', 'titulo_id', 'status', 'avaliacao', 'adicionado_em', 'atualizado_em']
        read_only_fields = ['adicionado_em', 'atualizado_em']

    # Devolve a avaliação do item em formato JSON, ou None (null) se não houver
    def get_avaliacao(self, item) -> dict | None:
        avaliacao = getattr(item, 'avaliacao', None)
        return AvaliacaoSerializer(avaliacao).data if avaliacao else None

    # validate() valida os dados como um todo antes de salvar
    def validate(self, attrs):
        # O "context" traz a requisição, de onde tiramos o usuário autenticado pelo token
        usuario = self.context['request'].user
        titulo = attrs.get('titulo')
        # self.instance é None na CRIAÇÃO (POST) e é o item existente na ALTERAÇÃO (PUT/PATCH)
        if self.instance is None:
            # Um usuário não pode ter o mesmo título duas vezes na biblioteca
            if ItemBiblioteca.objects.filter(usuario=usuario, titulo=titulo).exists():
                raise serializers.ValidationError({'titulo_id': 'Este título já está na sua biblioteca.'})
        # Na alteração, não é permitido trocar o título do item (apenas o status)
        elif titulo is not None and titulo != self.instance.titulo:
            raise serializers.ValidationError({'titulo_id': 'Não é possível trocar o título de um item; altere apenas o status.'})
        return attrs
