# proyectos/forms.py

from django import forms
from .models import Proyecto
from usuarios.models import Usuario

class ProyectoForm(forms.ModelForm):
    """Formulario para crear y editar proyectos"""
    
    # ← ESTE ES EL FIX: Recibir y manejar el argumento 'user'
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # ← Extrae 'user' antes de llamar super()
        super().__init__(*args, **kwargs)
        
        # Filtrar miembros según el rol
        if self.user:
            if self.user.rol == 'admin':
                # Admin puede agregar a cualquier usuario
                self.fields['miembros'].queryset = Usuario.objects.filter(
                    is_active=True
                )
            else:
                # Manager solo puede agregar usuarios activos
                self.fields['miembros'].queryset = Usuario.objects.filter(
                    is_active=True
                )
    
    class Meta:
        model = Proyecto
        fields = [
            'nombre',
            'descripcion',
            'estado',
            'fecha_inicio',
            'fecha_fin',
            'miembros'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del proyecto'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe el proyecto...'
            }),
            'estado': forms.Select(attrs={
                'class': 'form-select'
            }),
            'fecha_inicio': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'fecha_fin': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'miembros': forms.SelectMultiple(attrs={
                'class': 'form-select',
                'size': '5'
            }),
        }
        labels = {
            'nombre': 'Nombre del Proyecto',
            'descripcion': 'Descripción',
            'estado': 'Estado',
            'fecha_inicio': 'Fecha de Inicio',
            'fecha_fin': 'Fecha de Fin (opcional)',
            'miembros': 'Miembros del Equipo',
        }
    
    def clean(self):
        """Validaciones adicionales del formulario"""
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')
        
        # Validar que fecha_fin sea mayor que fecha_inicio
        if fecha_inicio and fecha_fin:
            if fecha_fin < fecha_inicio:
                raise forms.ValidationError(
                    'La fecha de fin no puede ser anterior a la fecha de inicio.'
                )
        
        return cleaned_data