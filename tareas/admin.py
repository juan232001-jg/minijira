from django.contrib import admin
from .models import Tarea

@admin.register(Tarea)
class TareaAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'proyecto', 'responsable', 'estado', 'prioridad', 'fecha_vencimiento', 'esta_vencida']
    list_filter = ['estado', 'prioridad', 'proyecto', 'fecha_vencimiento']
    search_fields = ['titulo', 'descripcion']
    readonly_fields = ['creado_en', 'actualizado_en', 'fecha_completado']
    
    def esta_vencida(self, obj):
        return '🔴 Sí' if obj.esta_vencida() else '✅ No'
    esta_vencida.short_description = 'Vencida'