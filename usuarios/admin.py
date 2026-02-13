from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'rol', 'is_staff']
    list_filter = ['rol', 'is_staff', 'is_active']
    fieldsets = UserAdmin.fieldsets + (
        ('Información Adicional', {
            'fields': ('rol', 'foto', 'telefono', 'empresa')
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información Adicional', {
            'fields': ('rol', 'foto', 'telefono', 'empresa')
        }),
    )