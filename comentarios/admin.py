"""
Configuración del panel de administración para la aplicación de Comentarios.
Permite supervisar la actividad de comunicación entre los miembros de los equipos.
"""

from django.contrib import admin
from .models import Comentario

@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    """
    Personalización del panel administrativo para los comentarios.
    Incluye una vista previa del texto y filtros por autor y fecha.
    """
    
    # Columnas principales para el listado administrativo
    list_display = ['tarea', 'usuario', 'texto_corto', 'creado_en']
    
    # Filtros laterales para la auditoría de comentarios
    list_filter = ['creado_en', 'usuario']
    
    # Capacidades de búsqueda por contenido y título de tarea
    search_fields = ['texto', 'tarea__titulo']
    
    # Protección de marcas de tiempo automáticas
    readonly_fields = ['creado_en', 'actualizado_en']
    
    def texto_corto(self, obj):
        """
        Genera un fragmento corto del texto del comentario para su visualización en tablas.
        """
        return obj.texto[:50] + '...' if len(obj.texto) > 50 else obj.texto
    
    # Nombre descriptivo de la columna de vista previa
    texto_corto.short_description = 'Vista previa'