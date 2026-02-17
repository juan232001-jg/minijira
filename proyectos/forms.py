"""
Formularios para la creación y edición de proyectos.
Incluye validación de fechas y filtrado de miembros del equipo según el rol del usuario.
"""

from django import forms
from .models import Proyecto
from usuarios.models import Usuario

class ProyectoForm(forms.ModelForm):
    """
    Formulario vinculado al modelo Proyecto.
    Implementa lógica personalizada en el constructor para restringir quiénes pueden ser miembros.
    """
    
    def __init__(self, *args, **kwargs):
        # Captura del usuario actual para la aplicación de lógica de negocio basada en roles
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filtrado de la lista de miembros potenciales
        if self.user:
            # Los miembros seleccionables deben ser usuarios activos en la plataforma
            self.fields['miembros'].queryset = Usuario.objects.filter(
                is_active=True
            ).order_by('first_name')
            # Nota: El administrador podría tener reglas adicionales, pero aquí se unifica a usuarios activos
    
    class Meta:
        """Metadatos y configuración de widgets para el formulario de Proyecto."""
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
        """
        Validación cruzada de campos. 
        Asegura que la cronología del proyecto (inicio y fin) sea lógica.
        """
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')
        
        # Restricción: La fecha de finalización no puede ocurrir antes de la fecha de inicio
        if fecha_inicio and fecha_fin:
            if fecha_fin < fecha_inicio:
                raise forms.ValidationError(
                    'La fecha de fin no puede ser anterior a la fecha de inicio.'
                )
        
        return cleaned_data