# Rotas do app relatorios (incluídas na raiz do site)
from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),               # /dashboard/  → painel com indicadores
    path('relatorio/', views.relatorio, name='relatorio'),               # /relatorio/  → relatório com filtros
    path('relatorio/csv/', views.relatorio_csv, name='relatorio_csv'),   # /relatorio/csv/ → download em CSV
]
