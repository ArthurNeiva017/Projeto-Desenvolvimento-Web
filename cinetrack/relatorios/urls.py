from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('relatorio/', views.relatorio, name='relatorio'),
    path('relatorio/csv/', views.relatorio_csv, name='relatorio_csv'),
]
