# Views do app tmdb: buscar títulos (catálogo local + API do TMDB) e importá-los para a biblioteca.
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from biblioteca.models import Genero, ItemBiblioteca, Titulo

from .forms import AdicionarDoCatalogoForm, BuscaTMDBForm, ImportarTMDBForm
# Funções que conversam com a API externa (ficam separadas em services.py)
from .services import TMDBErro, buscar_titulos, detalhar_titulo


def _adicionar_na_biblioteca(request, titulo, status):
    """Cria o item na biblioteca. Se já existir, avisa e oferece a edição (UC04 - 4a)."""
    # get_or_create: busca o item; se não existir, cria com os "defaults".
    # Devolve o objeto e um booleano "criado" (True se acabou de ser criado)
    item, criado = ItemBiblioteca.objects.get_or_create(
        usuario=request.user, titulo=titulo, defaults={'status': status},
    )
    if not criado:
        # O título já estava na biblioteca: leva o usuário para a tela de edição
        messages.warning(request, f'"{titulo.nome}" já está na sua biblioteca. Você pode editar o item abaixo.')
        return redirect('editar_item', id=item.id)
    messages.success(request, f'"{titulo.nome}" adicionado à biblioteca com sucesso!')
    return redirect('detalhe_item', id=item.id)


def _obter_genero(generos_tmdb):
    """Usa o primeiro gênero do TMDB como gênero principal do título."""
    # O loop só roda para o PRIMEIRO gênero, pois todos os caminhos dentro dele terminam em "return"
    for g in generos_tmdb:
        # 1) Tenta achar o gênero pelo ID do TMDB
        genero = Genero.objects.filter(tmdb_id=g['tmdb_id']).first()
        if genero:
            return genero
        # 2) Tenta achar pelo nome (ignorando maiúsculas/minúsculas)
        genero = Genero.objects.filter(nome__iexact=g['nome']).first()
        if genero:
            return genero
        # 3) Não existe ainda: cria o gênero (nome limitado a 60 caracteres, tamanho da coluna)
        return Genero.objects.create(nome=g['nome'][:60], tmdb_id=g['tmdb_id'])
    # Se o TMDB não informou nenhum gênero, usa o gênero "Outros"
    genero, _ = Genero.objects.get_or_create(nome='Outros')
    return genero


# Busca no catálogo local e no TMDB (UC05)
@login_required(login_url='login')
def buscar_tmdb(request):
    # O termo de busca vem pela URL (GET), ex.: /buscar/?q=duna&tipo=filme
    form = BuscaTMDBForm(request.GET or None)
    # Valores iniciais: listas vazias e nenhum erro
    resultados_locais, resultados_tmdb, erro_tmdb = [], [], None

    if form.is_valid():
        termo = form.cleaned_data['q']
        tipo = form.cleaned_data['tipo']

        # 1) Catálogo local (títulos já importados do TMDB por qualquer usuário)
        locais = Titulo.objects.filter(tmdb_id__isnull=False, nome__icontains=termo).select_related('genero')
        if tipo:
            locais = locais.filter(tipo=tipo)
        resultados_locais = list(locais[:10])  # no máximo 10 resultados
        # Conjunto (set) com os pares (tmdb_id, tipo) já existentes no catálogo,
        # usado para não mostrar o mesmo título duas vezes
        ja_no_catalogo = {(t.tmdb_id, t.tipo) for t in resultados_locais}

        # 2) API externa TMDB
        try:
            resultados_tmdb = [
                r for r in buscar_titulos(termo, tipo)
                if (r['tmdb_id'], r['tipo']) not in ja_no_catalogo
            ]
        except TMDBErro as erro:
            # UC05 - E1: exibe apenas os resultados locais e avisa o usuário
            erro_tmdb = str(erro)
            messages.warning(request, erro_tmdb)

        # Marca os títulos que já estão na biblioteca do usuário
        meus = ItemBiblioteca.objects.filter(usuario=request.user, titulo__tmdb_id__isnull=False)
        # values_list devolve apenas as colunas pedidas, em tuplas: (tmdb_id, tipo)
        na_biblioteca = {(t, tp) for t, tp in meus.values_list('titulo__tmdb_id', 'titulo__tipo')}
        # Adiciona um atributo/chave "na_biblioteca" em cada resultado, usado no template
        # para mostrar "Já está na biblioteca" em vez do botão de adicionar
        for t in resultados_locais:
            t.na_biblioteca = (t.tmdb_id, t.tipo) in na_biblioteca
        for r in resultados_tmdb:
            r['na_biblioteca'] = (r['tmdb_id'], r['tipo']) in na_biblioteca

    contexto = {
        'form': form,
        'buscou': form.is_bound and form.is_valid(),  # True se uma busca válida foi feita
        'resultados_locais': resultados_locais,
        'resultados_tmdb': resultados_tmdb,
        'erro_tmdb': erro_tmdb,
        'status_choices': ItemBiblioteca.STATUS_CHOICES,  # opções do select de status em cada resultado
    }
    return render(request, 'tmdb/buscar.html', contexto)


# Importa um título do TMDB e adiciona à biblioteca (UC04)
@login_required(login_url='login')
@require_POST  # só aceita envio de formulário (POST), pois altera dados
def importar_tmdb(request):
    form = ImportarTMDBForm(request.POST)
    if not form.is_valid():
        messages.error(request, 'Dados inválidos para importação.')
        return redirect('buscar_tmdb')

    tmdb_id = form.cleaned_data['tmdb_id']
    tipo = form.cleaned_data['tipo']
    status = form.cleaned_data['status']

    # Verifica se o título já foi importado antes (por este ou outro usuário)
    titulo = Titulo.objects.filter(tmdb_id=tmdb_id, tipo=tipo).first()
    if titulo is None:
        # Ainda não existe no catálogo: busca os detalhes completos no TMDB
        try:
            dados = detalhar_titulo(tmdb_id, tipo)
        except TMDBErro as erro:
            # UC04 - E1: informa a falha e oferece o cadastro manual
            messages.error(request, f'{erro} Você pode cadastrar o título manualmente.')
            return redirect('criar_item')

        # A gravação do título e do item é atômica (UC04 - requisitos especiais)
        with transaction.atomic():
            # Cria o título no catálogo local com os dados do TMDB
            # ([:200] e [:255] cortam os textos no tamanho máximo das colunas)
            titulo, _ = Titulo.objects.get_or_create(
                tmdb_id=tmdb_id, tipo=tipo,
                defaults={
                    'nome': dados['nome'][:200],
                    'genero': _obter_genero(dados['generos']),
                    'sinopse': dados['sinopse'],
                    'ano_lancamento': dados['ano_lancamento'],
                    'poster_url': dados['poster_url'][:255],
                },
            )
            return _adicionar_na_biblioteca(request, titulo, status)

    # Título já estava no catálogo: só adiciona na biblioteca do usuário
    return _adicionar_na_biblioteca(request, titulo, status)


# Adiciona um título que já está no catálogo local
@login_required(login_url='login')
@require_POST
def adicionar_do_catalogo(request):
    form = AdicionarDoCatalogoForm(request.POST)
    if not form.is_valid():
        messages.error(request, 'Dados inválidos.')
        return redirect('buscar_tmdb')
    # Só permite títulos importados do TMDB (tmdb_id não nulo); títulos manuais de outros usuários não aparecem
    titulo = get_object_or_404(Titulo, pk=form.cleaned_data['titulo_id'], tmdb_id__isnull=False)
    return _adicionar_na_biblioteca(request, titulo, form.cleaned_data['status'])
