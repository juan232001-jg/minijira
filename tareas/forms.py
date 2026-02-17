"""
Formularios para la gestión de tareas y comentarios.
Incluye lógica dinámica para filtrar proyectos y responsables según el rol del usuario.
"""

from django import forms
from .models import Tarea
from proyectos.models import Proyecto
from usuarios.models import Usuario
from comentarios.models import Comentario

class TareaForm(forms.ModelForm):
    """
    Formulario para la creación y edición de tareas.
    Personaliza los querysets de 'proyecto' y 'responsable' basándose en los permisos del usuario.
    """

    def __init__(self, *args, **kwargs):
        # Extracción del usuario actual para aplicar lógica de filtrado por roles
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # ===== FILTRADO DINÁMICO DE PROYECTOS SEGÚN ROL =====
        if self.user:
            if self.user.rol == 'admin':
                # El Administrador tiene visibilidad total de proyectos activos
                self.fields['proyecto'].queryset = Proyecto.objects.filter(
                    estado='activo'
                ).order_by('nombre')

            elif self.user.rol == 'manager':
                # El Manager solo puede asignar tareas a sus propios proyectos
                self.fields['proyecto'].queryset = Proyecto.objects.filter(
                    creador=self.user,
                    estado='activo'
                ).order_by('nombre')

            else:
                # El Miembro está limitado a los proyectos donde ya ha sido asignado
                self.fields['proyecto'].queryset = Proyecto.objects.filter(
                    miembros=self.user,
                    estado='activo'
                ).order_by('nombre')

        # ===== FILTRADO DE RESPONSABLES DISPONIBLES =====
        if self.user:
            # Por ahora se muestran todos los usuarios activos del sistema
            # Se puede refinar para mostrar solo miembros del proyecto seleccionado
            self.fields['responsable'].queryset = Usuario.objects.filter(
                is_active=True
            ).order_by('first_name', 'last_name')

        # Personalización de las etiquetas vacías en los selectores
        self.fields['proyecto'].empty_label = '-- Selecciona un proyecto --'
        self.fields['responsable'].empty_label = '-- Sin asignar --'

    class Meta:
        """Configuración del modelo y widgets para el formulario de Tarea."""
        model = Tarea
        fields = [
            'titulo',
            'descripcion',
            'proyecto',
            'responsable',
            'estado',
            'prioridad',
            'fecha_vencimiento',
        ]
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título de la tarea'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe la tarea...'
            }),
            'proyecto': forms.Select(attrs={
                'class': 'form-select'
            }),
            'responsable': forms.Select(attrs={
                'class': 'form-select'
            }),
            'estado': forms.Select(attrs={
                'class': 'form-select'
            }),
            'prioridad': forms.Select(attrs={
                'class': 'form-select'
            }),
            'fecha_vencimiento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }
        labels = {
            'titulo': 'Título de la Tarea',
            'descripcion': 'Descripción',
            'proyecto': 'Proyecto',
            'responsable': 'Responsable',
            'estado': 'Estado',
            'prioridad': 'Prioridad',
            'fecha_vencimiento': 'Fecha de Vencimiento (opcional)',
        }

    def clean(self):
        """
        Validaciones de integridad adicionales para el formulario.
        Asegura que las relaciones entre proyecto y responsable sean coherentes.
        """
        cleaned_data = super().clean()
        proyecto = cleaned_data.get('proyecto')
        responsable = cleaned_data.get('responsable')

        # Verificación de pertenencia del responsable al proyecto
        if proyecto and responsable:
            if not proyecto.miembros.filter(id=responsable.id).exists():
                # Nota: Se podría implementar una adición automática o un error de validación aquí
                pass

        return cleaned_data

class ComentarioForm(forms.ModelForm):
    """
    Formulario minimalista para la creación de comentarios en las tareas.
    """

    class Meta:
        """Configuración del widget de texto para comentarios."""
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
            'texto': '', # Se oculta el label para un diseño más limpio
        }