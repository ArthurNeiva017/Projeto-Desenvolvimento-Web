# Formulários (forms) do app biblioteca.
# Um form do Django faz três coisas: gera o HTML dos campos, recebe os dados
# enviados pelo usuário e valida esses dados antes de salvar no banco.

from datetime import date  # usado para saber o ano atual na validação do ano

from django import forms
from django.core.exceptions import ValidationError  # erro exibido ao usuário quando um campo é inválido

from .models import Genero, ItemBiblioteca, Titulo


# ModelForm: formulário gerado automaticamente a partir de um model (aqui, Titulo)
class TituloForm(forms.ModelForm):
    """Cadastro manual de um título, já escolhendo o status na biblioteca."""

    # Campo EXTRA que não existe no model Titulo (o status fica em ItemBiblioteca).
    # Ele é declarado à mão e tratado na view depois de salvar o título.
    status = forms.ChoiceField(
        choices=ItemBiblioteca.STATUS_CHOICES,
        initial=ItemBiblioteca.STATUS_QUERO,               # valor já selecionado ao abrir o form
        label='Status na biblioteca',
        widget=forms.Select(attrs={'class': 'form-select'}),  # 'form-select' é uma classe do Bootstrap
    )

    class Meta:
        model = Titulo  # model que o form vai criar/editar
        # Campos do model que aparecem no formulário (e na ordem em que aparecem)
        fields = ['nome', 'tipo', 'genero', 'ano_lancamento', 'sinopse', 'poster_url']
        # widgets: define qual elemento HTML será usado em cada campo e seus atributos (classes CSS, placeholder)
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex.: Cidade de Deus'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'genero': forms.Select(attrs={'class': 'form-select'}),
            'ano_lancamento': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ex.: 2002'}),
            'sinopse': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'poster_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
        }
        # labels: textos que aparecem acima de cada campo na tela
        labels = {
            'nome': 'Título',
            'tipo': 'Tipo',
            'genero': 'Gênero',
            'ano_lancamento': 'Ano de lançamento',
            'sinopse': 'Sinopse',
            'poster_url': 'URL do pôster',
        }

    # __init__ é executado sempre que o formulário é criado
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  # executa a criação padrão do ModelForm
        # Lista de opções do select de gênero = todos os gêneros do banco
        self.fields['genero'].queryset = Genero.objects.all()
        # Texto da primeira opção (vazia) do select
        self.fields['genero'].empty_label = 'Selecione um gênero'

    # Métodos "clean_<campo>" são validações personalizadas, chamadas por form.is_valid()
    def clean_nome(self):
        # strip() remove espaços em branco do início e do fim
        nome = self.cleaned_data['nome'].strip()
        if len(nome) < 2:
            raise ValidationError('O título deve ter pelo menos 2 caracteres.')
        return nome  # o valor retornado é o que fica salvo em cleaned_data

    def clean_ano_lancamento(self):
        ano = self.cleaned_data.get('ano_lancamento')
        # 1888 é o ano do filme mais antigo conhecido
        # Também aceitamos até 5 anos no futuro (lançamentos anunciados)
        if ano is not None and not (1888 <= ano <= date.today().year + 5):
            raise ValidationError('Informe um ano entre 1888 e %(max)s.', params={'max': date.today().year + 5})
        return ano

    def clean_poster_url(self):
        url = self.cleaned_data.get('poster_url', '')
        # Por segurança, só aceitamos imagens vindas de endereços HTTPS
        if url and not url.startswith('https://'):
            raise ValidationError('Use um endereço seguro (https://).')
        return url


class StatusForm(forms.ModelForm):
    """Alteração apenas do status (usado para títulos importados do TMDB)."""

    class Meta:
        model = ItemBiblioteca
        fields = ['status']  # apenas o campo status é editável
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'status': 'Status na biblioteca',
        }


# forms.Form (e não ModelForm): formulário comum, não ligado a um model.
# Serve apenas para ler e validar os filtros da busca.
class BuscaForm(forms.Form):
    """Filtros da busca na biblioteca (enviados por GET)."""

    # Texto livre para buscar pelo nome. required=False: o filtro é opcional
    q = forms.CharField(
        required=False, label='Buscar',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do filme ou série'}),
    )
    # Filtro por status. A opção ('', 'Todos os status') significa "sem filtro"
    status = forms.ChoiceField(
        required=False, label='Status',
        choices=[('', 'Todos os status')] + ItemBiblioteca.STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    # Filtro por tipo (filme ou série)
    tipo = forms.ChoiceField(
        required=False, label='Tipo',
        choices=[('', 'Filmes e séries')] + Titulo.TIPO_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    # ModelChoiceField: as opções vêm direto do banco (todos os gêneros cadastrados)
    genero = forms.ModelChoiceField(
        required=False, label='Gênero', queryset=Genero.objects.all(), empty_label='Todos os gêneros',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
