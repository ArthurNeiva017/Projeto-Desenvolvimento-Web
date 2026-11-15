# Views do app contas: página inicial, cadastro, login e logout de usuários.

from django.contrib import messages  # mensagens de aviso exibidas na próxima página
# Funções prontas do Django para autenticação:
# authenticate = confere usuário e senha | login = cria a sessão | logout = encerra a sessão
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User  # model de usuário padrão do Django
from django.contrib.auth.password_validation import validate_password  # aplica as regras de senha do settings.py
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST  # só aceita requisições POST



# Página inicial (landing page) do CineTrack
def index(request):
    return render(request, 'contas/index.html')


# Cadastro de novo usuário (UC01)
def register_view(request):
    # Se o usuário já está logado, não faz sentido se cadastrar de novo
    if request.user.is_authenticated:
        return redirect('index')

    # POST = o formulário de cadastro foi enviado
    if request.method == 'POST':
        # Lê os campos enviados pelo formulário. .get(campo, '') evita erro se o campo não vier.
        # .strip() remove espaços extras no começo e no fim
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        # Lista para acumular todos os erros e mostrá-los de uma vez
        erros = []
        if not username:
            erros.append('Informe um nome de usuário.')
        # username__iexact compara sem diferenciar maiúsculas/minúsculas ("Ana" == "ana")
        elif User.objects.filter(username__iexact=username).exists():
            erros.append('Este nome de usuário já está em uso.')
        if password != confirm_password:
            erros.append('As senhas não conferem!')
        else:

            # Valida a senha com as regras definidas em AUTH_PASSWORD_VALIDATORS
            # (tamanho mínimo, não ser parecida com o usuário, não ser comum, não ser só números)
            try:
                validate_password(password, User(username=username, email=email))
            except ValidationError as e:
                erros.extend(e.messages)  # adiciona todas as mensagens de erro da senha

        if erros:
            # Mostra cada erro como mensagem e devolve o formulário com os dados já digitados
            for erro in erros:
                messages.error(request, erro)
            return render(request, 'contas/register.html', {'username': username, 'email': email})

        # create_user salva o usuário com a senha CRIPTOGRAFADA (hash), nunca em texto puro
        User.objects.create_user(username=username, email=email, password=password)
        messages.success(request, 'Usuário criado com sucesso! Faça login para continuar.')
        return redirect('login')

    # GET = apenas abriu a página: mostra o formulário vazio
    return render(request, 'contas/register.html')


# Login do usuário (UC02)
def login_view(request):
    # Usuário já logado vai direto para a página inicial
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        # authenticate devolve o objeto User se usuário e senha estiverem corretos, ou None se não
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # login() grava o usuário na sessão (cookie), mantendo-o logado nas próximas páginas
            login(request, user)
            messages.success(request, f'Bem-vindo, {user.username}!')
            return redirect('dashboard')
        # Mensagem genérica: não revela se o erro foi no usuário ou na senha (mais seguro)
        messages.error(request, 'Usuário ou senha inválidos!')
        return render(request, 'contas/login.html', {'username': username})

    return render(request, 'contas/login.html')



# Logout: só por POST, para evitar que um simples link (GET) deslogue o usuário sem querer
@require_POST
def logout_view(request):
    logout(request)  # apaga os dados da sessão
    messages.success(request, 'Sessão encerrada.')
    return redirect('login')
