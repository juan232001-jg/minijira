

from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    """Modelo de usuario extendido"""
    
    ROLES = (
        ('admin', 'Administrador'),
        ('manager', 'Manager'),
        ('miembro', 'Miembro'),
    )
    
    rol = models.CharField(
        max_length=20, 
        choices=ROLES, 
        default='miembro',
        verbose_name='Rol'
    )
    foto = models.ImageField(
        upload_to='usuarios/', 
        null=True, 
        blank=True,
        verbose_name='Foto de perfil'
    )
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
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.username})"