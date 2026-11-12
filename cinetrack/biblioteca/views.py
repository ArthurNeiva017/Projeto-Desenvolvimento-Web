from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from .forms import BuscaForm, StatusForm, TituloForm
from .models import ItemBiblioteca


def _item_do_usuario(request, id):
    """Somente o dono do item pode ver, alterar ou remover (regra de domínio)."""
    return get_object_or_404(
        ItemBiblioteca.objects.select_related('titulo', 'titulo__genero'),
        pk=id, usuario=request.user,
    )


# Listagem e busca da biblioteca (UC03 e UC05)
@login_required(login_url='login')
def lista_biblioteca(request):
    itens = ItemBiblioteca.objects.filter(usuario=request.user).select_related('titulo', 'titulo__genero')

    form = BuscaForm(request.GET or None)
    if form.is_valid():
        q = form.cleaned_data.get('q')
        status = form.cleaned_data.get('status')
        tipo = form.cleaned_data.get('tipo')
        genero = form.cleaned_data.get('genero')
        if q:
            itens = itens.filter(titulo__nome__icontains=q)
        if status:
            itens = itens.filter(status=status)
        if tipo:
            itens = itens.filter(titulo__tipo=tipo)
        if genero:
            itens = itens.filter(titulo__genero=genero)

    contexto = {
        'itens': itens,
        'form': form,
        'filtrando': bool(request.GET),
    }
    return render(request, 'biblioteca/lista.html', contexto)


# Detalhes de um item (UC03)
@login_required(login_url='login')
def detalhe_item(request, id):
    item = _item_do_usuario(request, id)
    return render(request, 'biblioteca/detalhe.html', {'item': item})


# Cadastro manual de título na biblioteca (UC04)
@login_required(login_url='login')
def criar_item(request):
    if request.method == 'POST':
        form = TituloForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                titulo = form.save()
                ItemBiblioteca.objects.create(
                    usuario=request.user,
                    titulo=titulo,
                    status=form.cleaned_data['status'],
                )
            messages.success(request, f'"{titulo.nome}" adicionado à biblioteca com sucesso!')
            return redirect('lista_biblioteca')
        else:
            messages.error(request, 'Erro ao cadastrar o título. Verifique os dados informados.')
    else:
        form = TituloForm()
    return render(request, 'biblioteca/form.html', {'form': form})


# Edição de um item (UC06)
@login_required(login_url='login')
def editar_item(request, id):
    item = _item_do_usuario(request, id)
    titulo = item.titulo

    # Títulos importados do TMDB não têm os dados editados; apenas o status muda
    if titulo.importado_tmdb:
        form_class, instancia, inicial = StatusForm, item, {}
    else:
        form_class, instancia, inicial = TituloForm, titulo, {'status': item.status}

    if request.method == 'POST':
        form = form_class(request.POST, instance=instancia)
        if form.is_valid():
            with transaction.atomic():
                form.save()
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
        form = form_class(instance=instancia, initial=inicial)

    return render(request, 'biblioteca/form.html', {'form': form, 'editar': True, 'item': item})


# Remoção de um item (UC07)
@login_required(login_url='login')
def excluir_item(request, id):
    item = _item_do_usuario(request, id)
    if request.method == 'POST':
        nome = item.titulo.nome
        # A avaliação associada é removida junto (CASCADE); o título permanece no catálogo
        item.delete()
        messages.success(request, f'"{nome}" removido da biblioteca com sucesso!')
        return redirect('lista_biblioteca')
    return render(request, 'biblioteca/excluir.html', {'item': item})
