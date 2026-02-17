"""
Configuración del panel de administración para el modelo de Usuario.
Extiende la funcionalidad estándar de UserAdmin de Django para incluir los campos personalizados.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    """
    Personalización de la interfaz de administración para el modelo Usuario.
    Añade campos como rol, foto y empresa tanto en la visualización como en la edición.
    """
    
    # Campos que se muestran en la lista de usuarios del panel administrativo
    list_display = ['username', 'email', 'first_name', 'last_name', 'rol', 'is_staff']
    
    # Filtros laterales para facilitar la búsqueda en el panel administrativo
    list_filter = ['rol', 'is_staff', 'is_active']
    
    # Organización de los campos en el formulario de edición detallada
    fieldsets = UserAdmin.fieldsets + (
        ('Información Adicional', {
            'fields': ('rol', 'foto', 'telefono', 'empresa')
        }),
    )
    
    # Organización de los campos en el formulario de creación de nuevos usuarios
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información Adicional', {
            'fields': ('rol', 'foto', 'telefono', 'empresa')
        }),
    )