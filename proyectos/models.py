
from django.db import models
from django.conf import settings

class Proyecto(models.Model):
    """Modelo para proyectos"""
    
    ESTADOS = (
        ('activo', 'Activo'),
        ('pausado', 'Pausado'),
        ('completado', 'Completado'),
        ('cancelado', 'Cancelado'),
    )
    
    nombre = models.CharField(max_length=200, verbose_name='Nombre')
    descripcion = models.TextField(verbose_name='Descripción')
    estado = models.CharField(
        max_length=20, 
        choices=ESTADOS, 
        default='activo',
        verbose_name='Estado'
    )
    fecha_inicio = models.DateField(verbose_name='Fecha de inicio')
    fecha_fin = models.DateField(
        null=True, 
        blank=True,
        verbose_name='Fecha de fin'
    )
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
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Proyecto'
        verbose_name_plural = 'Proyectos'
        ordering = ['-creado_en']
    
    def __str__(self):
        return self.nombre
    
    def tareas_completadas(self):
        """Retorna el número de tareas completadas"""
        return self.tareas.filter(estado='completado').count()
    
    def total_tareas(self):
        """Retorna el total de tareas"""
        return self.tareas.count()
    
    def progreso(self):
        """Retorna el porcentaje de progreso"""
        total = self.total_tareas()
        if total == 0:
            return 0
        return int((self.tareas_completadas() / total) * 100)