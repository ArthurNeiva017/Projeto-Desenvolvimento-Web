import csv
from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count
from django.http import HttpResponse
from django.shortcuts import render

from biblioteca.models import Avaliacao, ItemBiblioteca

from .forms import RelatorioForm


def _filtrar_itens(request):
    """Aplica os filtros do relatório aos itens do usuário logado."""
    itens = (ItemBiblioteca.objects.filter(usuario=request.user)
             .select_related('titulo', 'titulo__genero', 'avaliacao')
             .order_by('titulo__nome'))
    form = RelatorioForm(request.GET or None)
    if form.is_bound and form.is_valid():
        f = form.cleaned_data
        if f['status']:
            itens = itens.filter(status=f['status'])
        if f['tipo']:
            itens = itens.filter(titulo__tipo=f['tipo'])
        if f['genero']:
            itens = itens.filter(titulo__genero=f['genero'])
        if f['data_inicio']:
            itens = itens.filter(adicionado_em__date__gte=f['data_inicio'])
        if f['data_fim']:
            itens = itens.filter(adicionado_em__date__lte=f['data_fim'])
    return form, itens


def _indicadores(itens):
    """Indicadores consolidados (RelatorioBiblioteca: não possui tabela própria)."""
    total = itens.count()
    por_status = {valor: 0 for valor, _ in ItemBiblioteca.STATUS_CHOICES}
    for linha in itens.values('status').annotate(qtd=Count('id')):
        por_status[linha['status']] = linha['qtd']
    por_tipo = {linha['titulo__tipo']: linha['qtd'] for linha in itens.values('titulo__tipo').annotate(qtd=Count('id'))}
    media = Avaliacao.objects.filter(item_biblioteca__in=itens).aggregate(media=Avg('nota'))['media']
    return {
        'total': total,
        'quero_assistir': por_status['quero_assistir'],
        'assistindo': por_status['assistindo'],
        'assistido': por_status['assistido'],
        'filmes': por_tipo.get('filme', 0),
        'series': por_tipo.get('serie', 0),
        'nota_media': round(media, 1) if media is not None else None,
        'avaliados': Avaliacao.objects.filter(item_biblioteca__in=itens).count(),
    }


# Dashboard com indicadores gerais (UC09)
@login_required(login_url='login')
def dashboard(request):
    itens = ItemBiblioteca.objects.filter(usuario=request.user)
    indicadores = _indicadores(itens)
    total = indicadores['total'] or 1
    status_grafico = [
        {'rotulo': rotulo, 'valor': valor, 'qtd': indicadores[valor], 'pct': round(indicadores[valor] * 100 / total)}
        for valor, rotulo in ItemBiblioteca.STATUS_CHOICES
    ]
    por_genero = (itens.values('titulo__genero__nome').annotate(qtd=Count('id')).order_by('-qtd', 'titulo__genero__nome')[:5])
    melhores = (Avaliacao.objects.filter(item_biblioteca__usuario=request.user)
                .select_related('item_biblioteca__titulo').order_by('-nota', '-criado_em')[:5])
    recentes = itens.select_related('titulo').order_by('-adicionado_em')[:5]

    contexto = {
        'ind': indicadores,
        'status_grafico': status_grafico,
        'por_genero': por_genero,
        'melhores': melhores,
        'recentes': recentes,
    }
    return render(request, 'relatorios/dashboard.html', contexto)


# Relatório com filtros, visualizável e imprimível (UC09)
@login_required(login_url='login')
def relatorio(request):
    form, itens = _filtrar_itens(request)
    if form.is_bound and not form.is_valid():
        messages.error(request, 'Verifique os filtros informados.')
    contexto = {
        'form': form,
        'itens': itens,
        'ind': _indicadores(itens),
        'gerado_em': date.today(),
        'query_string': request.GET.urlencode(),
    }
    return render(request, 'relatorios/relatorio.html', contexto)


def _celula_segura(valor):
    """Evita injeção de fórmulas ao abrir o CSV no Excel (CSV injection)."""
    texto = '' if valor is None else str(valor)
    if texto and texto[0] in ('=', '+', '-', '@', '\t', '\r'):
        return "'" + texto
    return texto


# Exportação do relatório em CSV (mesmos filtros da tela)
@login_required(login_url='login')
def relatorio_csv(request):
    _, itens = _filtrar_itens(request)
    resposta = HttpResponse(content_type='text/csv; charset=utf-8')
    resposta['Content-Disposition'] = f'attachment; filename="cinetrack-relatorio-{date.today():%Y%m%d}.csv"'
    resposta.write('﻿')  # BOM para o Excel reconhecer acentos

    escritor = csv.writer(resposta, delimiter=';')
    escritor.writerow(['Título', 'Tipo', 'Gênero', 'Ano', 'Status', 'Nota', 'Comentário', 'Adicionado em'])
    for item in itens:
        avaliacao = getattr(item, 'avaliacao', None)
        escritor.writerow([_celula_segura(v) for v in [
            item.titulo.nome,
            item.titulo.get_tipo_display(),
            item.titulo.genero.nome,
            item.titulo.ano_lancamento or '',
            item.get_status_display(),
            avaliacao.nota if avaliacao else '',
            avaliacao.comentario if avaliacao else '',
            item.adicionado_em.strftime('%d/%m/%Y'),
        ]])
    return resposta
