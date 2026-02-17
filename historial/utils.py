"""
Funciones de utilidad para el registro de eventos en el historial de tareas.
Centraliza la lógica de creación de registros históricos para diversos tipos de acciones.
"""

from .models import HistorialTarea

def registrar_cambio(tarea, usuario, tipo, descripcion,
                     valor_anterior=None, valor_nuevo=None):
    """
    Función base para crear un registro en el historial de una tarea.
    Captura todos los metadatos necesarios para la auditoría de cambios.
    """
    return HistorialTarea.objects.create(
        tarea=tarea,
        usuario=usuario,
        tipo=tipo,
        descripcion=descripcion,
        valor_anterior=valor_anterior,
        valor_nuevo=valor_nuevo,
    )

def registrar_creacion(tarea, usuario):
    """
    Registra el evento inicial de creación de una tarea.
    """
    registrar_cambio(
        tarea=tarea,
        usuario=usuario,
        tipo='creacion',
        descripcion=f'Tarea "{tarea.titulo}" creada en el proyecto "{tarea.proyecto.nombre}"',
    )

def registrar_cambio_estado(tarea, usuario, estado_anterior, estado_nuevo):
    """
    Registra específicamente los cambios en el flujo de trabajo (estados) de una tarea.
    """
    registrar_cambio(
        tarea=tarea,
        usuario=usuario,
        tipo='estado',
        descripcion=f'Estado cambiado de "{estado_anterior}" a "{estado_nuevo}"',
        valor_anterior=estado_anterior,
        valor_nuevo=estado_nuevo,
    )

def registrar_cambio_prioridad(tarea, usuario, prioridad_anterior, prioridad_nueva):
    """
    Registra modificaciones en el nivel de prioridad de una tarea.
    Utiliza etiquetas visuales amigables para la descripción.
    """
    etiquetas = {
        'baja':     '🟢 Baja',
        'media':    '🔵 Media',
        'alta':     '🟠 Alta',
        'urgente':  '🔴 Urgente',
    }
    registrar_cambio(
        tarea=tarea,
        usuario=usuario,
        tipo='prioridad',
        descripcion=f'Prioridad cambiada de "{etiquetas.get(prioridad_anterior)}" a "{etiquetas.get(prioridad_nueva)}"',
        valor_anterior=prioridad_anterior,
        valor_nuevo=prioridad_nueva,
    )

def registrar_cambio_responsable(tarea, usuario, responsable_anterior, responsable_nuevo):
    """
    Registra cambios en la asignación de responsables para una tarea.
    Gestiona casos donde el responsable previo o nuevo sea nulo (sin asignar).
    """
    nombre_anterior = responsable_anterior.get_full_name() if responsable_anterior else 'Sin asignar'
    nombre_nuevo = responsable_nuevo.get_full_name() if responsable_nuevo else 'Sin asignar'
    
    registrar_cambio(
        tarea=tarea,
        usuario=usuario,
        tipo='asignacion',
        descripcion=f'Responsable cambiado de "{nombre_anterior}" a "{nombre_nuevo}"',
        valor_anterior=str(responsable_anterior.pk) if responsable_anterior else None,
        valor_nuevo=str(responsable_nuevo.pk) if responsable_nuevo else None,
    )

def registrar_edicion(tarea, usuario):
    """
    Registra ediciones generales en los metadatos de una tarea.
    """
    registrar_cambio(
        tarea=tarea,
        usuario=usuario,
        tipo='edicion',
        descripcion=f'Tarea "{tarea.titulo}" editada',
    )

def registrar_comentario(tarea, usuario):
    """
    Registra la adición de un nuevo comentario como parte del historial de actividad.
    """
    registrar_cambio(
        tarea=tarea,
        usuario=usuario,
        tipo='comentario',
        descripcion=f'{usuario.get_full_name()} agregó un comentario',
    )