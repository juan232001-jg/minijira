"""
Definición del modelo de Proyectos para la organización de tareas y equipos de trabajo.
Permite el seguimiento de estados globales y el cálculo dinámico del progreso.
"""

from django.db import models
from django.conf import settings

class Proyecto(models.Model):
    """
    Representa un proyecto dentro del sistema. 
    Actúa como contenedor de tareas y define los miembros participantes y el creador responsable.
    """
    
    # Estados globales permitidos para un proyecto
    ESTADOS = (
        ('activo', 'Activo'),
        ('pausado', 'Pausado'),
        ('completado', 'Completado'),
        ('cancelado', 'Cancelado'),
    )
    
    # Atributos básicos del proyecto
    nombre = models.CharField(max_length=200, verbose_name='Nombre')
    descripcion = models.TextField(verbose_name='Descripción')
    
    # Seguimiento del estado de ejecución
    estado = models.CharField(
        max_length=20, 
        choices=ESTADOS, 
        default='activo',
        verbose_name='Estado'
    )
    
    # Planificación temporal de hitos del proyecto
    fecha_inicio = models.DateField(verbose_name='Fecha de inicio')
    fecha_fin = models.DateField(
        null=True, 
        blank=True,
        verbose_name='Fecha de fin'
    )
    
    # Relaciones con usuarios (Creador y Equipo de trabajo)
    creador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='proyectos_creados',
        verbose_name='Creador'
    )
    miembros = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='proyectos',
        blank=True,
        verbose_name='Miembros'
    )
    
    # Timestamps automáticos para control de auditoría
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    class Meta:
        """Metadatos para el modelo Proyecto."""
        verbose_name = 'Proyecto'
        verbose_name_plural = 'Proyectos'
        ordering = ['-creado_en']
    
    def __str__(self):
        """Retorna el nombre del proyecto como su representación textual."""
        return self.nombre
    
    def tareas_completadas(self):
        """
        Calcula la cantidad de tareas asociadas al proyecto que han sido finalizadas.
        """
        return self.tareas.filter(estado='completado').count()
    
    def total_tareas(self):
        """
        Calcula el volumen total de tareas registradas para este proyecto.
        """
        return self.tareas.count()
    
    def progreso(self):
        """
        Calcula el porcentaje de avance del proyecto basado en la relación entre
        tareas completadas y el total de tareas existentes.
        """
        total = self.total_tareas()
        if total == 0:
            return 0
        return int((self.tareas_completadas() / total) * 100)