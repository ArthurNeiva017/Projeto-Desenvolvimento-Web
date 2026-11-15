# Views do app biblioteca.
# Uma view é uma função que recebe a requisição (request) do navegador
# e devolve uma resposta: normalmente uma página HTML (render) ou um redirecionamento (redirect).

from django.contrib import messages  # mensagens de aviso (sucesso/erro) mostradas na próxima página
from django.contrib.auth.decorators import login_required  # bloqueia acesso de quem não está logado
from django.db import transaction  # permite agrupar várias operações no banco em uma só (tudo ou nada)
from django.shortcuts import get_object_or_404, redirect, render

from .forms import BuscaForm, StatusForm, TituloForm
from .models import ItemBiblioteca


def _item_do_usuario(request, id):
    """Somente o dono do item pode ver, alterar ou remover (regra de domínio)."""
    # Busca o item pelo id E pelo usuário logado. Se o item não existir ou for de
    # outra pessoa, o Django responde com erro 404 (página não encontrada).
    # select_related já traz o título e o gênero na mesma consulta SQL (JOIN),
    # evitando consultas extras ao banco.
    return get_object_or_404(
        ItemBiblioteca.objects.select_related('titulo', 'titulo__genero'),
        pk=id, usuario=request.user,
    )


# Listagem e busca da biblioteca (UC03 e UC05)
# @login_required: se o usuário não estiver logado, é enviado para a página de login
@login_required(login_url='login')
def lista_biblioteca(request):
    # Começa com TODOS os itens do usuário logado
    itens = ItemBiblioteca.objects.filter(usuario=request.user).select_related('titulo', 'titulo__genero')

    # Os filtros chegam pela URL (request.GET), ex.: /biblioteca/?q=matrix&status=assistido
    # "or None" faz o form ficar vazio (não validado) quando não há filtros na URL
    form = BuscaForm(request.GET or None)
    if form.is_valid():
        # cleaned_data contém os valores já validados e convertidos
        q = form.cleaned_data.get('q')
        status = form.cleaned_data.get('status')
        tipo = form.cleaned_data.get('tipo')
        genero = form.cleaned_data.get('genero')
        # Cada filtro só é aplicado se foi preenchido. Os filtros vão se acumulando.
        if q:
            # icontains = "contém", sem diferenciar maiúsculas/minúsculas
            # titulo__nome = acessa o campo "nome" do título relacionado
            itens = itens.filter(titulo__nome__icontains=q)
        if status:
            itens = itens.filter(status=status)
        if tipo:
            itens = itens.filter(titulo__tipo=tipo)
        if genero:
            itens = itens.filter(titulo__genero=genero)

    # Contexto: dicionário com as variáveis que o template HTML poderá usar
    contexto = {
        'itens': itens,
        'form': form,
        'filtrando': bool(request.GET),  # True se algum filtro foi enviado (muda a mensagem de "lista vazia")
    }
    return render(request, 'biblioteca/lista.html', contexto)


# Detalhes de um item (UC03)
@login_required(login_url='login')
def detalhe_item(request, id):
    # O "id" vem da URL, ex.: /biblioteca/5/
    item = _item_do_usuario(request, id)
    return render(request, 'biblioteca/detalhe.html', {'item': item})


# Cadastro manual de título na biblioteca (UC04)
@login_required(login_url='login')
def criar_item(request):
    # POST = o usuário enviou o formulário preenchido
    if request.method == 'POST':
        form = TituloForm(request.POST)  # preenche o form com os dados enviados
        if form.is_valid():  # roda todas as validações (incluindo os métodos clean_*)
            # transaction.atomic(): se algo der errado no meio, nada é salvo
            # (não fica um título "solto" sem item na biblioteca)
            with transaction.atomic():
                titulo = form.save()  # 1) cria o Título no catálogo
                ItemBiblioteca.objects.create(  # 2) adiciona o título na biblioteca do usuário
                    usuario=request.user,
                    titulo=titulo,
                    status=form.cleaned_data['status'],
                )
            messages.success(request, f'"{titulo.nome}" adicionado à biblioteca com sucesso!')
            # Redireciona para a lista (padrão Post/Redirect/Get: evita reenviar o form ao atualizar a página)
            return redirect('lista_biblioteca')
        else:
            messages.error(request, 'Erro ao cadastrar o título. Verifique os dados informados.')
    else:
        # GET = o usuário apenas abriu a página; mostramos o formulário vazio
        form = TituloForm()
    return render(request, 'biblioteca/form.html', {'form': form})


# Edição de um item (UC06)
@login_required(login_url='login')
def editar_item(request, id):
    item = _item_do_usuario(request, id)
    titulo = item.titulo

    # Títulos importados do TMDB não têm os dados editados; apenas o status muda
    # Por isso escolhemos qual formulário usar e qual objeto ele vai editar:
    if titulo.importado_tmdb:
        # Importado: edita só o status do ItemBiblioteca
        form_class, instancia, inicial = StatusForm, item, {}
    else:
        # Manual: edita os dados do Título + o status (campo extra, com valor inicial atual)
        form_class, instancia, inicial = TituloForm, titulo, {'status': item.status}

    if request.method == 'POST':
        # instance=instancia faz o form ATUALIZAR o objeto existente, em vez de criar um novo
        form = form_class(request.POST, instance=instancia)
        if form.is_valid():
            with transaction.atomic():
                form.save()
                # No TituloForm o status não é salvo automaticamente (não é campo do Titulo),
                # então atualizamos o item da biblioteca manualmente
                if form_class is TituloForm:
                    item.status = form.cleaned_data['status']
                    item.save()
            messages.success(request, 'Título alterado com sucesso!')
            # UC06 - 5a: ao marcar como assistido, o sistema oferece a avaliação
            if item.status == ItemBiblioteca.STATUS_ASSISTIDO:
                messages.info(request, 'Você marcou como assistido. Que tal avaliar este título?')
            return redirect('detalhe_item', id=item.id)
        else:
            messages.error(request, 'Erro ao alterar o título. Verifique os dados informados.')
    else:
        # GET: mostra o formulário já preenchido com os dados atuais
        form = form_class(instance=instancia, initial=inicial)

    # O mesmo template de cadastro é reaproveitado; 'editar': True muda os textos da página
    return render(request, 'biblioteca/form.html', {'form': form, 'editar': True, 'item': item})


# Remoção de um item (UC07)
@login_required(login_url='login')
def excluir_item(request, id):
    item = _item_do_usuario(request, id)
    # Só exclui quando o usuário confirma (POST). No GET mostramos a página de confirmação.
    if request.method == 'POST':
        nome = item.titulo.nome  # guarda o nome antes de apagar, para usar na mensagem
        # A avaliação associada é removida junto (CASCADE); o título permanece no catálogo
        item.delete()
        messages.success(request, f'"{nome}" removido da biblioteca com sucesso!')
        return redirect('lista_biblioteca')
    return render(request, 'biblioteca/excluir.html', {'item': item})
