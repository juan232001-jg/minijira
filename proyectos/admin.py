"""
Configuración del panel de administración para el modelo de Proyectos.
Permite una gestión centralizada y la visualización rápida del avance y estados.
"""

from django.contrib import admin
from .models import Proyecto

@admin.register(Proyecto)
class ProyectoAdmin(admin.ModelAdmin):
    """
    Personalización del panel de administración para Proyectos.
    Facilita el manejo de relaciones ManyToMany y el monitoreo del progreso porcentual.
    """
    
    # Definición de las columnas visibles en el listado de proyectos
    list_display = ['nombre', 'estado', 'creador', 'fecha_inicio', 'progreso']
    
    # Filtros laterales para segmentación por estado y fecha
    list_filter = ['estado', 'fecha_inicio']
    
    # Campos habilitados para búsqueda global
    search_fields = ['nombre', 'descripcion']
    
    # Widget mejorado para la gestión de múltiples miembros
    filter_horizontal = ['miembros']
    
    # Campos de auditoría protegidos contra edición
    readonly_fields = ['creado_en', 'actualizado_en']
    
    def progreso(self, obj):
        """
        Retorna una representación formateada del porcentaje de avance para la interfaz administrativa.
        """
        return f"{obj.progreso()}%"
    
    # Título amigable para la columna del porcentaje de progreso
    progreso.short_description = 'Progreso'