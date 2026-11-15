# Formulário com os filtros do relatório da biblioteca.
from django import forms
from django.core.exceptions import ValidationError

from biblioteca.models import Genero, ItemBiblioteca, Titulo


# forms.Form comum (não está ligado a um model): só lê e valida os filtros
class RelatorioForm(forms.Form):
    # Todos os filtros são opcionais (required=False); a opção '' significa "Todos"
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
    # Opções vindas do banco: todos os gêneros cadastrados
    genero = forms.ModelChoiceField(
        required=False, label='Gênero', queryset=Genero.objects.all(), empty_label='Todos',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    # Período em que o item foi adicionado. type='date' mostra o calendário do navegador
    data_inicio = forms.DateField(
        required=False, label='Adicionado de',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
    )
    data_fim = forms.DateField(
        required=False, label='até',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
    )

    # clean() (sem nome de campo) valida o formulário como um todo,
    # útil quando a regra envolve MAIS DE UM campo ao mesmo tempo
    def clean(self):
        dados = super().clean()
        inicio, fim = dados.get('data_inicio'), dados.get('data_fim')
        # A data inicial não pode ser depois da data final
        if inicio and fim and inicio > fim:
            raise ValidationError('A data inicial deve ser anterior à data final.')
        return dados
