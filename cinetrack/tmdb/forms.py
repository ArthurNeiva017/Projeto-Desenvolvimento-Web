from django import forms

from biblioteca.models import ItemBiblioteca, Titulo


class BuscaTMDBForm(forms.Form):
    q = forms.CharField(
        label='Nome do filme ou série', min_length=2, max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex.: Duna'}),
        error_messages={'min_length': 'Digite pelo menos 2 caracteres.', 'required': 'Digite o nome do título.'},
    )
    tipo = forms.ChoiceField(
        label='Tipo', required=False,
        choices=[('', 'Filmes e séries')] + Titulo.TIPO_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    def clean_q(self):
        return self.cleaned_data['q'].strip()


class ImportarTMDBForm(forms.Form):
    tmdb_id = forms.IntegerField(min_value=1, widget=forms.HiddenInput)
    tipo = forms.ChoiceField(choices=Titulo.TIPO_CHOICES, widget=forms.HiddenInput)
    status = forms.ChoiceField(choices=ItemBiblioteca.STATUS_CHOICES, initial=ItemBiblioteca.STATUS_QUERO)


class AdicionarDoCatalogoForm(forms.Form):
    titulo_id = forms.IntegerField(min_value=1, widget=forms.HiddenInput)
    status = forms.ChoiceField(choices=ItemBiblioteca.STATUS_CHOICES, initial=ItemBiblioteca.STATUS_QUERO)
