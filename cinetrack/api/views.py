"""
API REST do CineTrack (Django REST Framework).

Rotas públicas (somente leitura): gêneros e títulos do catálogo.
Rotas protegidas por JWT: biblioteca do usuário autenticado.
"""
from django.db.models import Avg, Count
# drf_spectacular: gera a documentação automática da API (Swagger/Redoc).
# Os decorators extend_schema apenas descrevem as rotas na documentação; não mudam o comportamento.
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from biblioteca.models import Avaliacao, Genero, ItemBiblioteca, Titulo

from .serializers import AvaliacaoSerializer, GeneroSerializer, ItemBibliotecaSerializer, TituloSerializer


# ViewSet = uma classe que agrupa várias ações de uma rota (listar, detalhar, criar, alterar, excluir).
# ReadOnlyModelViewSet oferece apenas as ações de leitura: list (GET /generos/) e retrieve (GET /generos/1/)
@extend_schema_view(
    list=extend_schema(summary='Lista os gêneros', tags=['Catálogo']),
    retrieve=extend_schema(summary='Detalha um gênero', tags=['Catálogo']),
)
class GeneroViewSet(viewsets.ReadOnlyModelViewSet):
    """Gêneros usados para classificar os títulos."""
    queryset = Genero.objects.all()           # registros que a rota expõe
    serializer_class = GeneroSerializer       # como converter cada registro para JSON
    permission_classes = [permissions.AllowAny]  # rota pública: não precisa de login


@extend_schema_view(
    list=extend_schema(
        summary='Lista os títulos do catálogo',
        tags=['Catálogo'],
        # Documenta os filtros aceitos na URL, ex.: /api/v1/titulos/?busca=duna&tipo=filme
        parameters=[
            OpenApiParameter('busca', OpenApiTypes.STR, description='Parte do nome do título'),
            OpenApiParameter('tipo', OpenApiTypes.STR, enum=['filme', 'serie'], description='Filme ou série'),
            OpenApiParameter('genero', OpenApiTypes.INT, description='ID do gênero'),
            OpenApiParameter('ano', OpenApiTypes.INT, description='Ano de lançamento'),
        ],
    ),
    retrieve=extend_schema(summary='Detalha um título', tags=['Catálogo']),
)
class TituloViewSet(viewsets.ReadOnlyModelViewSet):
    """Catálogo de filmes e séries do CineTrack."""
    serializer_class = TituloSerializer
    permission_classes = [permissions.AllowAny]

    # Sobrescrevendo o método para listar os títulos e adicionar os filtros
    def get_queryset(self):
        queryset = Titulo.objects.select_related('genero').all()
        # query_params = parâmetros da URL (o que vem depois do "?")
        params = self.request.query_params

        busca = params.get('busca')
        if busca:
            queryset = queryset.filter(nome__icontains=busca)
        tipo = params.get('tipo')
        if tipo:
            queryset = queryset.filter(tipo__iexact=tipo)
        genero = params.get('genero')
        # isdigit() garante que o valor é numérico antes de converter (evita erro com texto)
        if genero and genero.isdigit():
            queryset = queryset.filter(genero_id=int(genero))
        ano = params.get('ano')
        if ano and ano.isdigit():
            queryset = queryset.filter(ano_lancamento=int(ano))
        return queryset


@extend_schema_view(
    list=extend_schema(
        summary='Lista a biblioteca do usuário autenticado',
        parameters=[
            OpenApiParameter('status', OpenApiTypes.STR, enum=['quero_assistir', 'assistindo', 'assistido']),
            OpenApiParameter('tipo', OpenApiTypes.STR, enum=['filme', 'serie']),
        ],
    ),
    create=extend_schema(summary='Adiciona um título do catálogo à biblioteca'),
    retrieve=extend_schema(summary='Detalha um item da biblioteca'),
    update=extend_schema(summary='Altera o status de um item (PUT)'),
    partial_update=extend_schema(summary='Altera o status de um item (PATCH)'),
    destroy=extend_schema(summary='Remove um item da biblioteca (e a sua avaliação)'),
)
@extend_schema(tags=['Biblioteca (JWT)'])
# ModelViewSet oferece o CRUD completo: GET, POST, PUT, PATCH e DELETE
class ItemBibliotecaViewSet(viewsets.ModelViewSet):
    """Biblioteca pessoal. Exige o cabeçalho Authorization: Bearer <token>."""
    queryset = ItemBiblioteca.objects.none()  # usado apenas pela documentação (Swagger)
    serializer_class = ItemBibliotecaSerializer
    # Define que este ViewSet exige um token JWT válido
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]  # sem token válido → erro 401

    def get_queryset(self):
        # Cada usuário só enxerga e altera a própria biblioteca
        queryset = (ItemBiblioteca.objects.filter(usuario=self.request.user)
                    .select_related('titulo', 'titulo__genero', 'avaliacao'))
        # Filtros opcionais pela URL: ?status=assistido&tipo=filme
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)
        tipo = self.request.query_params.get('tipo')
        if tipo:
            queryset = queryset.filter(titulo__tipo=tipo)
        return queryset

    # Chamado ao criar um item (POST): define o dono como o usuário do token,
    # impedindo que alguém crie itens na biblioteca de outra pessoa
    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

    # --- Ação personalizada: avaliar um item ---
    # @action cria uma rota extra. detail=True → rota de um item específico:
    # POST /api/v1/biblioteca/{id}/avaliar/
    @extend_schema(summary='Registra ou altera a avaliação do item', request=AvaliacaoSerializer,
                   responses={200: AvaliacaoSerializer, 201: AvaliacaoSerializer})
    @action(detail=True, methods=['post'])
    def avaliar(self, request, pk=None):
        # get_object() busca o item usando o get_queryset (ou seja, só itens do próprio usuário)
        item = self.get_object()
        avaliacao = Avaliacao.objects.filter(item_biblioteca=item).first()
        # Se já houver avaliação, o serializer a atualiza; senão, cria uma nova
        serializer = AvaliacaoSerializer(avaliacao, data=request.data)
        # raise_exception=True: se os dados forem inválidos, responde automaticamente com erro 400
        serializer.is_valid(raise_exception=True)
        serializer.save(item_biblioteca=item)
        # 200 OK = avaliação alterada | 201 Created = avaliação criada
        codigo = status.HTTP_200_OK if avaliacao else status.HTTP_201_CREATED
        return Response(serializer.data, status=codigo)

    # --- Ação personalizada: relatório da biblioteca ---
    # detail=False → rota da coleção: GET /api/v1/biblioteca/relatorio/
    @extend_schema(summary='Indicadores consolidados da biblioteca', responses={200: OpenApiTypes.OBJECT})
    @action(detail=False, methods=['get'])
    def relatorio(self, request):
        itens = ItemBiblioteca.objects.filter(usuario=request.user)
        # Contagem por status (GROUP BY status), começando todos com zero
        por_status = {valor: 0 for valor, _ in ItemBiblioteca.STATUS_CHOICES}
        for linha in itens.values('status').annotate(qtd=Count('id')):
            por_status[linha['status']] = linha['qtd']
        # Contagem por tipo (filme/série)
        por_tipo = {linha['titulo__tipo']: linha['qtd'] for linha in itens.values('titulo__tipo').annotate(qtd=Count('id'))}
        # Média das notas do usuário
        media = Avaliacao.objects.filter(item_biblioteca__usuario=request.user).aggregate(media=Avg('nota'))['media']
        dados = {
            'usuario': request.user.username,
            'total': itens.count(),
            'por_status': por_status,
            'por_tipo': {'filme': por_tipo.get('filme', 0), 'serie': por_tipo.get('serie', 0)},
            'nota_media': round(media, 1) if media is not None else None,
        }
        # Response converte o dicionário em JSON automaticamente
        return Response(dados)
