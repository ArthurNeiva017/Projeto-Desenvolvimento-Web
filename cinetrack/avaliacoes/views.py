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
    item = get_object_or_404(ItemBiblioteca.objects.select_related('titulo'), pk=id, usuario=request.user)
    avaliacao = Avaliacao.objects.filter(item_biblioteca=item).first()

    if request.method == 'POST':
        form = AvaliacaoForm(request.POST, instance=avaliacao)
        if form.is_valid():
            nova = form.save(commit=False)
            nova.item_biblioteca = item
            nova.save()
            messages.success(request, 'Avaliação salva com sucesso!')
            return redirect('detalhe_item', id=item.id)
        else:
            messages.error(request, 'Erro ao salvar a avaliação. Verifique os dados informados.')
    else:
        form = AvaliacaoForm(instance=avaliacao)

    return render(request, 'avaliacoes/form.html', {'form': form, 'item': item, 'editar': avaliacao is not None})


# Remover a avaliação de um item
@login_required(login_url='login')
@require_POST
def excluir_avaliacao(request, id):
    item = get_object_or_404(ItemBiblioteca, pk=id, usuario=request.user)
    removidas, _ = Avaliacao.objects.filter(item_biblioteca=item).delete()
    if removidas:
        messages.success(request, 'Avaliação removida com sucesso!')
    return redirect('detalhe_item', id=item.id)
