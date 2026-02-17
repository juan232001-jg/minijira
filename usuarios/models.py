from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    """
    Modelo de usuario personalizado que extiende AbstractUser de Django.
    Permite gestionar información adicional del usuario como roles, fotos de perfil y datos de contacto.
    """
    
    # Definición de roles disponibles en el sistema
    ROLES = (
        ('admin', 'Administrador'),
        ('manager', 'Manager'),
        ('miembro', 'Miembro'),
    )
    
    # Campo para definir el nivel de acceso del usuario
    rol = models.CharField(
        max_length=20, 
        choices=ROLES, 
        default='miembro',
        verbose_name='Rol'
    )
    
    # Imagen de perfil del usuario, almacenada en el directorio 'usuarios/'
    foto = models.ImageField(
        upload_to='usuarios/', 
        null=True, 
        blank=True,
        verbose_name='Foto de perfil'
    )
    
    # Información de contacto y organizacional
    telefono = models.CharField(
        max_length=20, 
        blank=True,
        verbose_name='Teléfono'
    )
    empresa = models.CharField(
        max_length=100, 
        blank=True,
        verbose_name='Empresa'
    )
    
    class Meta:
        """Configuraciones adicionales para el modelo Usuario."""
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
    
    def __str__(self):
        """Retorna una representación en cadena del usuario (Nombre completo y username)."""
        return f"{self.get_full_name()} ({self.username})"