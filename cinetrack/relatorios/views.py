# Views do app relatorios: dashboard com indicadores, relatório filtrado e exportação CSV.
import csv  # biblioteca padrão do Python para gerar arquivos CSV
from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
# Avg (média) e Count (contagem) são funções de agregação executadas pelo próprio banco (SQL)
from django.db.models import Avg, Count
from django.http import HttpResponse
from django.shortcuts import render

from biblioteca.models import Avaliacao, ItemBiblioteca

from .forms import RelatorioForm


def _filtrar_itens(request):
    """Aplica os filtros do relatório aos itens do usuário logado."""
    # Itens do usuário, já trazendo título, gênero e avaliação na mesma consulta, ordenados por nome
    itens = (ItemBiblioteca.objects.filter(usuario=request.user)
             .select_related('titulo', 'titulo__genero', 'avaliacao')
             .order_by('titulo__nome'))
    # Filtros vêm pela URL (GET). Sem filtros, o form fica "não vinculado" (None)
    form = RelatorioForm(request.GET or None)
    # is_bound = o form recebeu dados; is_valid = os dados passaram nas validações
    if form.is_bound and form.is_valid():
        f = form.cleaned_data
        if f['status']:
            itens = itens.filter(status=f['status'])
        if f['tipo']:
            itens = itens.filter(titulo__tipo=f['tipo'])
        if f['genero']:
            itens = itens.filter(titulo__genero=f['genero'])
        # __date pega só a data do DateTime; __gte = maior ou igual (>=); __lte = menor ou igual (<=)
        if f['data_inicio']:
            itens = itens.filter(adicionado_em__date__gte=f['data_inicio'])
        if f['data_fim']:
            itens = itens.filter(adicionado_em__date__lte=f['data_fim'])
    # Devolve o form (para reexibir os filtros na tela) e os itens filtrados
    return form, itens


def _indicadores(itens):
    """Indicadores consolidados (RelatorioBiblioteca: não possui tabela própria)."""
    total = itens.count()  # SELECT COUNT(*)
    # Começa com todos os status zerados, ex.: {'quero_assistir': 0, 'assistindo': 0, 'assistido': 0}
    por_status = {valor: 0 for valor, _ in ItemBiblioteca.STATUS_CHOICES}
    # values('status').annotate(Count) equivale a "GROUP BY status" no SQL:
    # devolve uma linha por status com a quantidade (qtd)
    for linha in itens.values('status').annotate(qtd=Count('id')):
        por_status[linha['status']] = linha['qtd']
    # Mesma ideia, agrupando por tipo (filme/série)
    por_tipo = {linha['titulo__tipo']: linha['qtd'] for linha in itens.values('titulo__tipo').annotate(qtd=Count('id'))}
    # Média das notas das avaliações desses itens. aggregate devolve um dicionário: {'media': 7.5}
    media = Avaliacao.objects.filter(item_biblioteca__in=itens).aggregate(media=Avg('nota'))['media']
    return {
        'total': total,
        'quero_assistir': por_status['quero_assistir'],
        'assistindo': por_status['assistindo'],
        'assistido': por_status['assistido'],
        'filmes': por_tipo.get('filme', 0),   # .get(..., 0): se não houver filmes, vale 0
        'series': por_tipo.get('serie', 0),
        # Arredonda para 1 casa decimal; None quando ainda não há nenhuma avaliação
        'nota_media': round(media, 1) if media is not None else None,
        'avaliados': Avaliacao.objects.filter(item_biblioteca__in=itens).count(),
    }


# Dashboard com indicadores gerais (UC09)
@login_required(login_url='login')
def dashboard(request):
    itens = ItemBiblioteca.objects.filter(usuario=request.user)
    indicadores = _indicadores(itens)
    # "or 1" evita divisão por zero quando a biblioteca está vazia
    total = indicadores['total'] or 1
    # Dados para as barras de progresso por status: rótulo, quantidade e porcentagem
    status_grafico = [
        {'rotulo': rotulo, 'valor': valor, 'qtd': indicadores[valor], 'pct': round(indicadores[valor] * 100 / total)}
        for valor, rotulo in ItemBiblioteca.STATUS_CHOICES
    ]
    # Top 5 gêneros com mais títulos (GROUP BY gênero, ordenado pela quantidade decrescente)
    # O [:5] vira um LIMIT 5 no SQL
    por_genero = (itens.values('titulo__genero__nome').annotate(qtd=Count('id')).order_by('-qtd', 'titulo__genero__nome')[:5])
    # Top 5 títulos mais bem avaliados pelo usuário
    melhores = (Avaliacao.objects.filter(item_biblioteca__usuario=request.user)
                .select_related('item_biblioteca__titulo').order_by('-nota', '-criado_em')[:5])
    # Os 5 itens adicionados mais recentemente
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
    # Se o usuário enviou filtros inválidos (ex.: data inicial depois da final), avisa
    if form.is_bound and not form.is_valid():
        messages.error(request, 'Verifique os filtros informados.')
    contexto = {
        'form': form,
        'itens': itens,
        'ind': _indicadores(itens),  # indicadores calculados só sobre os itens filtrados
        'gerado_em': date.today(),
        # Filtros atuais em formato de URL (ex.: "status=assistido&tipo=filme"),
        # usados no link de exportar CSV para manter os mesmos filtros
        'query_string': request.GET.urlencode(),
    }
    return render(request, 'relatorios/relatorio.html', contexto)


def _celula_segura(valor):
    """Evita injeção de fórmulas ao abrir o CSV no Excel (CSV injection)."""
    texto = '' if valor is None else str(valor)
    # Se o texto começar com um caractere que o Excel interpreta como fórmula,
    # colocamos um apóstrofo na frente para ele ser tratado como texto comum
    if texto and texto[0] in ('=', '+', '-', '@', '\t', '\r'):
        return "'" + texto
    return texto


# Exportação do relatório em CSV (mesmos filtros da tela)
@login_required(login_url='login')
def relatorio_csv(request):
    _, itens = _filtrar_itens(request)  # o "_" ignora o form, que não é necessário aqui
    # Em vez de uma página HTML, a resposta é um arquivo CSV
    resposta = HttpResponse(content_type='text/csv; charset=utf-8')
    # "attachment" faz o navegador baixar o arquivo, com nome contendo a data (ex.: ...-20261115.csv)
    resposta['Content-Disposition'] = f'attachment; filename="cinetrack-relatorio-{date.today():%Y%m%d}.csv"'
    resposta.write('﻿')  # BOM para o Excel reconhecer acentos

    # O csv.writer escreve direto na resposta HTTP. ";" é o separador usado pelo Excel em português
    escritor = csv.writer(resposta, delimiter=';')
    # Primeira linha: cabeçalho das colunas
    escritor.writerow(['Título', 'Tipo', 'Gênero', 'Ano', 'Status', 'Nota', 'Comentário', 'Adicionado em'])
    for item in itens:
        # getattr com valor padrão: devolve None se o item não tiver avaliação (evita erro)
        avaliacao = getattr(item, 'avaliacao', None)
        # Uma linha por item; cada valor passa pela proteção contra CSV injection
        escritor.writerow([_celula_segura(v) for v in [
            item.titulo.nome,
            item.titulo.get_tipo_display(),
            item.titulo.genero.nome,
            item.titulo.ano_lancamento or '',
            item.get_status_display(),
            avaliacao.nota if avaliacao else '',
            avaliacao.comentario if avaliacao else '',
            item.adicionado_em.strftime('%d/%m/%Y'),  # data no formato brasileiro
        ]])
    return resposta
