"""
Configuración del panel de administración para el modelo de Tareas.
Permite la visualización rápida de estados, prioridades y el seguimiento de vencimientos.
"""

from django.contrib import admin
from .models import Tarea

@admin.register(Tarea)
class TareaAdmin(admin.ModelAdmin):
    """
    Personalización de la interfaz administrativa para Tareas.
    Incluye indicadores visuales de vencimiento y filtros por proyecto y estado.
    """
    
    # Columnas visibles en el listado principal
    list_display = ['titulo', 'proyecto', 'responsable', 'estado', 'prioridad', 'fecha_vencimiento', 'esta_vencida']
    
    # Filtros disponibles para segmentar las tareas
    list_filter = ['estado', 'prioridad', 'proyecto', 'fecha_vencimiento']
    
    # Campos que permiten la búsqueda por texto
    search_fields = ['titulo', 'descripcion']
    
    # Campos protegidos contra edición manual para mantener la integridad de la auditoría
    readonly_fields = ['creado_en', 'actualizado_en', 'fecha_completado']
    
    def esta_vencida(self, obj):
        """
        Calcula y muestra un indicador visual amigable sobre el estado de vencimiento de la tarea.
        """
        return '🔴 Sí' if obj.esta_vencida() else '✅ No'
    
    # Configuración de metadatos para la columna del indicador de vencimiento
    esta_vencida.short_description = 'Vencida'