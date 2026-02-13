# tareas/forms.py

from django import forms
from .models import Tarea
from proyectos.models import Proyecto
from comentarios.models import Comentario

class TareaForm(forms.ModelForm):
    """Formulario para crear y editar tareas"""
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filtrar proyectos solo del usuario
        if self.user:
            self.fields['proyecto'].queryset = Proyecto.objects.filter(miembros=self.user)
    
    class Meta:
        model = Tarea
        fields = ['titulo', 'descripcion', 'proyecto', 'responsable', 'estado', 'prioridad', 'fecha_vencimiento']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'proyecto': forms.Select(attrs={'class': 'form-select'}),
            'responsable': forms.Select(attrs={'class': 'form-select'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'prioridad': forms.Select(attrs={'class': 'form-select'}),
            'fecha_vencimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
        labels = {
            'titulo': 'Título de la Tarea',
            'descripcion': 'Descripción',
            'proyecto': 'Proyecto',
            'responsable': 'Responsable',
            'estado': 'Estado',
            'prioridad': 'Prioridad',
            'fecha_vencimiento': 'Fecha de Vencimiento',
        }

class ComentarioForm(forms.ModelForm):
    """Formulario para comentarios"""
    
    class Meta:
        model = Comentario
        fields = ['texto']
        widgets = {
            'texto': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Escribe un comentario...'
            }),
        }
        labels = {
            'texto': '',
        }