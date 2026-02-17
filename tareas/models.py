"""
Definición del modelo de Tareas para la gestión de actividades dentro de los proyectos.
Incluye lógica para el seguimiento de estados, prioridades, responsables y fechas de vencimiento.
"""

from django.db import models
from django.conf import settings
from django.utils import timezone
from proyectos.models import Proyecto

class Tarea(models.Model):
    """
    Representa una unidad de trabajo asignada a un usuario dentro de un proyecto específico.
    Gestiona el ciclo de vida de la tarea mediante estados y prioridades.
    """
    
    # Posibles estados de una tarea durante su ejecución
    ESTADOS = (
        ('pendiente', 'Pendiente'),
        ('en_progreso', 'En Progreso'),
        ('en_revision', 'En Revisión'),
        ('completado', 'Completado'),
    )
    
    # Niveles de importancia/urgencia de la tarea
    PRIORIDADES = (
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
        ('urgente', 'Urgente'),
    )
    
    # Información básica de la tarea
    titulo = models.CharField(max_length=200, verbose_name='Título')
    descripcion = models.TextField(verbose_name='Descripción')
    
    # Relación con el proyecto al que pertenece
    proyecto = models.ForeignKey(
        Proyecto,
        on_delete=models.CASCADE,
        related_name='tareas',
        verbose_name='Proyecto'
    )
    
    # Usuario encargado de ejecutar la tarea
    responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tareas_asignadas',
        verbose_name='Responsable'
    )
    
    # Usuario que registró la tarea en el sistema
    creador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tareas_creadas',
        verbose_name='Creador'
    )
    
    # Atributos de seguimiento y control
    estado = models.CharField(
        max_length=20, 
        choices=ESTADOS, 
        default='pendiente',
        verbose_name='Estado'
    )
    prioridad = models.CharField(
        max_length=20, 
        choices=PRIORIDADES, 
        default='media',
        verbose_name='Prioridad'
    )
    
    # Control de tiempos y plazos
    fecha_vencimiento = models.DateField(
        null=True, 
        blank=True,
        verbose_name='Fecha de vencimiento'
    )
    fecha_completado = models.DateTimeField(
        null=True, 
        blank=True,
        verbose_name='Fecha de completado'
    )
    
    # Timestamps automáticos de auditoría
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    class Meta:
        """Metadatos del modelo Tarea."""
        verbose_name = 'Tarea'
        verbose_name_plural = 'Tareas'
        ordering = ['-creado_en']
    
    def __str__(self):
        """Retorna el título de la tarea como representación textual del objeto."""
        return self.titulo
    
    def esta_vencida(self):
        """
        Evalúa si la tarea ha superado su fecha límite sin haber sido completada.
        """
        if self.fecha_vencimiento and self.estado != 'completado':
            return timezone.now().date() > self.fecha_vencimiento
        return False
    
    def save(self, *args, **kwargs):
        """
        Extiende el método save para registrar automáticamente la fecha de finalización
        cuando el estado cambia a 'completado'.
        """
        if self.estado == 'completado' and not self.fecha_completado:
            self.fecha_completado = timezone.now()
        super().save(*args, **kwargs)