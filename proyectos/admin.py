from django.contrib import admin
from .models import Proyecto

@admin.register(Proyecto)
class ProyectoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'estado', 'creador', 'fecha_inicio', 'progreso']
    list_filter = ['estado', 'fecha_inicio']
    search_fields = ['nombre', 'descripcion']
    filter_horizontal = ['miembros']
    readonly_fields = ['creado_en', 'actualizado_en']
    
    def progreso(self, obj):
        return f"{obj.progreso()}%"
    progreso.short_description = 'Progreso'