"""
Definición del modelo de Historial para el seguimiento de auditoría de las tareas.
Registra cada cambio significativo, permitiendo mantener una trazabilidad detallada de la ejecución.
"""

from django.db import models
from django.conf import settings
from tareas.models import Tarea

class HistorialTarea(models.Model):
    """
    Entidad que almacena el registro histórico de acciones sobre una tarea.
    Captura el tipo de cambio, los valores antes y después de la acción, y el usuario responsable.
    """

    # Categorías de eventos que se registran en el historial
    TIPOS = (
        ('estado',       'Cambio de Estado'),
        ('prioridad',    'Cambio de Prioridad'),
        ('asignacion',   'Cambio de Responsable'),
        ('creacion',     'Tarea Creada'),
        ('edicion',      'Tarea Editada'),
        ('comentario',   'Comentario Agregado'),
        ('eliminacion',  'Tarea Eliminada'),
    )

    # Relación con la tarea afectada
    tarea = models.ForeignKey(
        Tarea,
        on_delete=models.CASCADE,
        related_name='historial',
        verbose_name='Tarea'
    )
    
    # Usuario que ejecutó la acción que originó el registro
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Usuario'
    )
    
    # Especificación del tipo de evento ocurrido
    tipo = models.CharField(
        max_length=20,
        choices=TIPOS,
        verbose_name='Tipo de cambio'
    )
    
    # Almacenamiento opcional de valores para registrar la evolución del campo afectado
    valor_anterior = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Valor anterior'
    )
    valor_nuevo = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Valor nuevo'
    )
    
    # Detalle descriptivo de la acción realizada
    descripcion = models.TextField(
        verbose_name='Descripción'
    )
    
    # Marca de tiempo automática del registro
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Metadatos para el modelo Historial de Tareas."""
        verbose_name = 'Historial'
        verbose_name_plural = 'Historial de Tareas'
        ordering = ['-creado_en']

    def __str__(self):
        """Retorna una cadena descriptiva del registro histórico."""
        return f'{self.tarea.titulo} - {self.get_tipo_display()}'