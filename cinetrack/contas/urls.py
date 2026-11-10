from django.urls import path
from . import views

urlpatterns = [
    # página inicial do CineTrack
    path('', views.index, name='index'),
    # permitir o fluxo de login
    path('login/', views.login_view, name='login'),
    # permitir o fluxo de logout
    path('logout/', views.logout_view, name='logout'),
    # permitir o cadastro de um novo usuário
    path('register/', views.register_view, name='register'),
]
