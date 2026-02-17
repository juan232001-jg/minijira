"""
Definición del modelo de Comentarios para facilitar la comunicación en las tareas.
Permite a los miembros del equipo dejar observaciones o actualizaciones en cada tarea.
"""

from django.db import models
from django.conf import settings
from tareas.models import Tarea

class Comentario(models.Model):
    """
    Representa una entrada de texto realizada por un usuario vinculada a una tarea específica.
    Se utiliza para el seguimiento colaborativo y la comunicación del equipo.
    """
    
    # Referencia a la tarea comentada
    tarea = models.ForeignKey(
        Tarea,
        on_delete=models.CASCADE,
        related_name='comentarios',
        verbose_name='Tarea'
    )
    
    # Usuario autor del comentario
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comentarios',
        verbose_name='Usuario'
    )
    
    # Contenido textual del comentario
    texto = models.TextField(verbose_name='Comentario')
    
    # Marcas de tiempo para control de actividad
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    class Meta:
        """Metadatos para el modelo Comentario."""
        verbose_name = 'Comentario'
        verbose_name_plural = 'Comentarios'
        ordering = ['creado_en']
    
    def __str__(self):
        """Retorna una breve identificación del autor y la tarea asociada."""
        return f"Comentario de {self.usuario.username} en {self.tarea.titulo}"