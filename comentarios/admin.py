from django.contrib import admin
from .models import Comentario

@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    list_display = ['tarea', 'usuario', 'texto_corto', 'creado_en']
    list_filter = ['creado_en', 'usuario']
    search_fields = ['texto', 'tarea__titulo']
    readonly_fields = ['creado_en', 'actualizado_en']
    
    def texto_corto(self, obj):
        return obj.texto[:50] + '...' if len(obj.texto) > 50 else obj.texto
    texto_corto.short_description = 'Comentario'