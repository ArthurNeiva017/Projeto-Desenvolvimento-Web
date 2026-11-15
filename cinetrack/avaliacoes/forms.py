# Formulário de avaliação (nota + comentário) de um item da biblioteca.
from django import forms
from django.core.exceptions import ValidationError

# O model Avaliacao fica no app biblioteca; aqui apenas o reutilizamos
from biblioteca.models import Avaliacao


# ModelForm gerado a partir do model Avaliacao
class AvaliacaoForm(forms.ModelForm):
    class Meta:
        model = Avaliacao
        fields = ['nota', 'comentario']  # o item_biblioteca é definido na view, não pelo usuário
        widgets = {
            # min/max no HTML: o navegador já impede valores fora de 0 a 10
            'nota': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 10}),
            'comentario': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'maxlength': 255,
                                                'placeholder': 'O que você achou? (opcional)'}),
        }
        labels = {
            'nota': 'Nota (0 a 10)',
            'comentario': 'Comentário',
        }

    # Validação no servidor (não dá para confiar só na validação do navegador)
    def clean_nota(self):
        nota = self.cleaned_data.get('nota')
        if nota is None or not (0 <= nota <= 10):
            raise ValidationError('A nota deve estar entre 0 e 10.')
        return nota

    # Remove espaços extras do comentário antes de salvar
    def clean_comentario(self):
        return self.cleaned_data.get('comentario', '').strip()
