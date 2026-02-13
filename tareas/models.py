# tareas/models.py

from django.db import models
from django.conf import settings
from django.utils import timezone
from proyectos.models import Proyecto

class Tarea(models.Model):
    """Modelo para tareas"""
    
    ESTADOS = (
        ('pendiente', 'Pendiente'),
        ('en_progreso', 'En Progreso'),
        ('en_revision', 'En Revisión'),
        ('completado', 'Completado'),
    )
    
    PRIORIDADES = (
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
        ('urgente', 'Urgente'),
    )
    
    titulo = models.CharField(max_length=200, verbose_name='Título')
    descripcion = models.TextField(verbose_name='Descripción')
    proyecto = models.ForeignKey(
        Proyecto,
        on_delete=models.CASCADE,
        related_name='tareas',
        verbose_name='Proyecto'
    )
    responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tareas_asignadas',
        verbose_name='Responsable'
    )
    creador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tareas_creadas',
        verbose_name='Creador'
    )
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
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Tarea'
        verbose_name_plural = 'Tareas'
        ordering = ['-creado_en']
    
    def __str__(self):
        return self.titulo
    
    def esta_vencida(self):
        """Verifica si la tarea está vencida"""
        if self.fecha_vencimiento and self.estado != 'completado':
            return timezone.now().date() > self.fecha_vencimiento
        return False
    
    def save(self, *args, **kwargs):
        """Guarda la fecha de completado automáticamente"""
        if self.estado == 'completado' and not self.fecha_completado:
            self.fecha_completado = timezone.now()
        super().save(*args, **kwargs)