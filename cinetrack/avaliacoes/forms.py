from django import forms
from django.core.exceptions import ValidationError

from biblioteca.models import Avaliacao


class AvaliacaoForm(forms.ModelForm):
    class Meta:
        model = Avaliacao
        fields = ['nota', 'comentario']
        widgets = {
            'nota': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 10}),
            'comentario': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'maxlength': 255,
                                                'placeholder': 'O que você achou? (opcional)'}),
        }
        labels = {
            'nota': 'Nota (0 a 10)',
            'comentario': 'Comentário',
        }

    def clean_nota(self):
        nota = self.cleaned_data.get('nota')
        if nota is None or not (0 <= nota <= 10):
            raise ValidationError('A nota deve estar entre 0 e 10.')
        return nota

    def clean_comentario(self):
        return self.cleaned_data.get('comentario', '').strip()
