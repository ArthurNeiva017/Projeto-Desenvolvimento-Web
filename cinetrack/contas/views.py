from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST


# Página inicial
def index(request):
    return render(request, 'contas/index.html')


# Página de registro
def register_view(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        # Valores informados no cadastro
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        erros = []
        if not username:
            erros.append('Informe um nome de usuário.')
        elif User.objects.filter(username__iexact=username).exists():
            erros.append('Este nome de usuário já está em uso.')
        if password != confirm_password:
            erros.append('As senhas não conferem!')
        else:
            # Aplica as regras de senha definidas em AUTH_PASSWORD_VALIDATORS
            try:
                validate_password(password, User(username=username, email=email))
            except ValidationError as e:
                erros.extend(e.messages)

        if erros:
            for erro in erros:
                messages.error(request, erro)
            return render(request, 'contas/register.html', {'username': username, 'email': email})

        # Inclusão no banco de dados do novo usuário (a senha é salva com hash)
        User.objects.create_user(username=username, email=email, password=password)
        messages.success(request, 'Usuário criado com sucesso! Faça login para continuar.')
        return redirect('login')

    return render(request, 'contas/register.html')


# Página de login
def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        # Método para verificar as credenciais
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)  # cria a sessão
            messages.success(request, f'Bem-vindo, {user.username}!')
            return redirect('index')
        messages.error(request, 'Usuário ou senha inválidos!')
        return render(request, 'contas/login.html', {'username': username})

    return render(request, 'contas/login.html')


# Logout (somente via POST, protegido por CSRF)
@require_POST
def logout_view(request):
    logout(request)
    messages.success(request, 'Sessão encerrada.')
    return redirect('login')
