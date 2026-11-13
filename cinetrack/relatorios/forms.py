from django import forms
from django.core.exceptions import ValidationError

from biblioteca.models import Genero, ItemBiblioteca, Titulo


class RelatorioForm(forms.Form):
    status = forms.ChoiceField(
        required=False, label='Status',
        choices=[('', 'Todos')] + ItemBiblioteca.STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    tipo = forms.ChoiceField(
        required=False, label='Tipo',
        choices=[('', 'Todos')] + Titulo.TIPO_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    genero = forms.ModelChoiceField(
        required=False, label='Gênero', queryset=Genero.objects.all(), empty_label='Todos',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    data_inicio = forms.DateField(
        required=False, label='Adicionado de',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
    )
    data_fim = forms.DateField(
        required=False, label='até',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
    )

    def clean(self):
        dados = super().clean()
        inicio, fim = dados.get('data_inicio'), dados.get('data_fim')
        if inicio and fim and inicio > fim:
            raise ValidationError('A data inicial deve ser anterior à data final.')
        return dados
