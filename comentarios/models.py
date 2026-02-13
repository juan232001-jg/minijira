# comentarios/models.py

from django.db import models
from django.conf import settings
from tareas.models import Tarea

class Comentario(models.Model):
    """Modelo para comentarios en tareas"""
    
    tarea = models.ForeignKey(
        Tarea,
        on_delete=models.CASCADE,
        related_name='comentarios',
        verbose_name='Tarea'
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comentarios',
        verbose_name='Usuario'
    )
    texto = models.TextField(verbose_name='Comentario')
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Comentario'
        verbose_name_plural = 'Comentarios'
        ordering = ['creado_en']
    
    def __str__(self):
        return f"Comentario de {self.usuario.username} en {self.tarea.titulo}"