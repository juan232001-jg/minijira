"""
Configuración del panel de administración para el Historial de Tareas.
Provee una interfaz para auditar los cambios realizados en el sistema por los usuarios.
"""

from django.contrib import admin
from .models import HistorialTarea

@admin.register(HistorialTarea)
class HistorialAdmin(admin.ModelAdmin):
    """
    Personalización de la interfaz administrativa para el historial.
    Configura la visualización de eventos de auditoría y filtros por tipo de acción.
    """
    
    # Columnas visibles para la auditoría rápida en el listado
    list_display = ['tarea', 'usuario', 'tipo', 'descripcion', 'creado_en']
    
    # Filtros para facilitar la segmentación de eventos históricos
    list_filter  = ['tipo', 'creado_en']
    
    # Búsqueda habilitada por título de tarea y descripción del cambio
    search_fields = ['tarea__titulo', 'descripcion']
    
    # Garantiza la integridad de la marca de tiempo impidiendo modificaciones
    readonly_fields = ['creado_en']