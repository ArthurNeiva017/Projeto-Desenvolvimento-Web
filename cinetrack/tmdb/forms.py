# Formulários do app tmdb (busca e importação de títulos).
from django import forms

from biblioteca.models import ItemBiblioteca, Titulo


# Formulário da busca: nome do título + tipo (opcional)
class BuscaTMDBForm(forms.Form):
    q = forms.CharField(
        label='Nome do filme ou série', min_length=2, max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex.: Duna'}),
        # Mensagens de erro personalizadas, em português
        error_messages={'min_length': 'Digite pelo menos 2 caracteres.', 'required': 'Digite o nome do título.'},
    )
    tipo = forms.ChoiceField(
        label='Tipo', required=False,
        choices=[('', 'Filmes e séries')] + Titulo.TIPO_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    # Remove espaços extras do termo pesquisado
    def clean_q(self):
        return self.cleaned_data['q'].strip()


# Formulário enviado ao clicar em "Adicionar" num resultado vindo do TMDB.
# tmdb_id e tipo ficam em campos ocultos (HiddenInput); o usuário só escolhe o status.
class ImportarTMDBForm(forms.Form):
    tmdb_id = forms.IntegerField(min_value=1, widget=forms.HiddenInput)
    tipo = forms.ChoiceField(choices=Titulo.TIPO_CHOICES, widget=forms.HiddenInput)
    status = forms.ChoiceField(choices=ItemBiblioteca.STATUS_CHOICES, initial=ItemBiblioteca.STATUS_QUERO)


# Formulário enviado ao adicionar um título que JÁ existe no catálogo local (usa o id do banco)
class AdicionarDoCatalogoForm(forms.Form):
    titulo_id = forms.IntegerField(min_value=1, widget=forms.HiddenInput)
    status = forms.ChoiceField(choices=ItemBiblioteca.STATUS_CHOICES, initial=ItemBiblioteca.STATUS_QUERO)
