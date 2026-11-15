# Views do app avaliacoes: criar, alterar e remover a avaliação de um item.
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from biblioteca.models import Avaliacao, ItemBiblioteca

from .forms import AvaliacaoForm


# Registrar ou alterar a avaliação de um item (UC08)
@login_required(login_url='login')
def avaliar_item(request, id):
    # Somente o dono do item pode avaliar
    # (filtra por usuario=request.user; item de outra pessoa → erro 404)
    item = get_object_or_404(ItemBiblioteca.objects.select_related('titulo'), pk=id, usuario=request.user)
    # Procura uma avaliação já existente. .first() devolve None se não houver nenhuma
    avaliacao = Avaliacao.objects.filter(item_biblioteca=item).first()

    if request.method == 'POST':
        # Se "avaliacao" existir, o form a ATUALIZA; se for None, o form CRIA uma nova
        form = AvaliacaoForm(request.POST, instance=avaliacao)
        if form.is_valid():
            # commit=False: monta o objeto mas ainda NÃO salva no banco,
            # para podermos preencher o item_biblioteca antes
            nova = form.save(commit=False)
            nova.item_biblioteca = item
            nova.save()  # agora sim salva no banco
            messages.success(request, 'Avaliação salva com sucesso!')
            return redirect('detalhe_item', id=item.id)
        else:
            messages.error(request, 'Erro ao salvar a avaliação. Verifique os dados informados.')
    else:
        # GET: mostra o formulário (preenchido, se já existir avaliação)
        form = AvaliacaoForm(instance=avaliacao)

    # 'editar' indica ao template se é uma avaliação nova ou uma alteração
    return render(request, 'avaliacoes/form.html', {'form': form, 'item': item, 'editar': avaliacao is not None})


# Remover a avaliação de um item
@login_required(login_url='login')
@require_POST  # exclusão só por POST (formulário com botão), nunca por um simples link
def excluir_avaliacao(request, id):
    item = get_object_or_404(ItemBiblioteca, pk=id, usuario=request.user)
    # delete() devolve uma tupla: (quantidade de registros apagados, detalhes por model)
    removidas, _ = Avaliacao.objects.filter(item_biblioteca=item).delete()
    if removidas:
        messages.success(request, 'Avaliação removida com sucesso!')
    return redirect('detalhe_item', id=item.id)
