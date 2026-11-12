from datetime import date

from django import forms
from django.core.exceptions import ValidationError

from .models import Genero, ItemBiblioteca, Titulo


class TituloForm(forms.ModelForm):
    """Cadastro manual de um título, já escolhendo o status na biblioteca."""

    status = forms.ChoiceField(
        choices=ItemBiblioteca.STATUS_CHOICES,
        initial=ItemBiblioteca.STATUS_QUERO,
        label='Status na biblioteca',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    class Meta:
        model = Titulo
        fields = ['nome', 'tipo', 'genero', 'ano_lancamento', 'sinopse', 'poster_url']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex.: Cidade de Deus'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'genero': forms.Select(attrs={'class': 'form-select'}),
            'ano_lancamento': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ex.: 2002'}),
            'sinopse': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'poster_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
        }
        labels = {
            'nome': 'Título',
            'tipo': 'Tipo',
            'genero': 'Gênero',
            'ano_lancamento': 'Ano de lançamento',
            'sinopse': 'Sinopse',
            'poster_url': 'URL do pôster',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['genero'].queryset = Genero.objects.all()
        self.fields['genero'].empty_label = 'Selecione um gênero'

    def clean_nome(self):
        nome = self.cleaned_data['nome'].strip()
        if len(nome) < 2:
            raise ValidationError('O título deve ter pelo menos 2 caracteres.')
        return nome

    def clean_ano_lancamento(self):
        ano = self.cleaned_data.get('ano_lancamento')
        # 1888 é o ano do filme mais antigo conhecido
        if ano is not None and not (1888 <= ano <= date.today().year + 5):
            raise ValidationError('Informe um ano entre 1888 e %(max)s.', params={'max': date.today().year + 5})
        return ano

    def clean_poster_url(self):
        url = self.cleaned_data.get('poster_url', '')
        if url and not url.startswith('https://'):
            raise ValidationError('Use um endereço seguro (https://).')
        return url


class StatusForm(forms.ModelForm):
    """Alteração apenas do status (usado para títulos importados do TMDB)."""

    class Meta:
        model = ItemBiblioteca
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'status': 'Status na biblioteca',
        }


class BuscaForm(forms.Form):
    """Filtros da busca na biblioteca (enviados por GET)."""

    q = forms.CharField(
        required=False, label='Buscar',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do filme ou série'}),
    )
    status = forms.ChoiceField(
        required=False, label='Status',
        choices=[('', 'Todos os status')] + ItemBiblioteca.STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    tipo = forms.ChoiceField(
        required=False, label='Tipo',
        choices=[('', 'Filmes e séries')] + Titulo.TIPO_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    genero = forms.ModelChoiceField(
        required=False, label='Gênero', queryset=Genero.objects.all(), empty_label='Todos os gêneros',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
