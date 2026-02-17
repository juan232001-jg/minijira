"""
Vistas para la gestión del ciclo de vida de las tareas.
Incluye creación, edición, visualización detallada, eliminación y cambio de estado,
así como filtrado avanzado por diversos criterios.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from .models import Tarea
from .forms import TareaForm, ComentarioForm
from comentarios.models import Comentario
from usuarios.permisos import VerificarPermiso, admin_o_manager
from historial.models import HistorialTarea
from historial.utils import (
    registrar_creacion,
    registrar_cambio_estado,
    registrar_cambio_prioridad,
    registrar_cambio_responsable,
    registrar_edicion,
    registrar_comentario,
)

@login_required
def tarea_lista(request):
    """
    Despliega la lista de tareas filtradas según el rol del usuario:
    - Admin: Acceso global a todas las tareas.
    - Manager: Tareas pertenecientes a proyectos creados por él.
    - Miembro: Tareas asignadas en proyectos donde participa.
    
    Permite además filtrar por estado, prioridad y búsqueda por texto.
    """
    user = request.user
    
    # Lógica de visibilidad inicial basada en el rol
    if user.rol == 'admin':
        tareas = Tarea.objects.all().order_by('-creado_en')
    elif user.rol == 'manager':
        tareas = Tarea.objects.filter(proyecto__creador=user).order_by('-creado_en')
    else:
        tareas = Tarea.objects.filter(proyecto__miembros=user).order_by('-creado_en')
    
    # Captura de parámetros de filtrado desde la URL
    filtro_estado = request.GET.get('estado', '')
    filtro_prioridad = request.GET.get('prioridad', '')
    filtro_orden = request.GET.get('orden', 'reciente')
    busqueda = request.GET.get('busqueda', '')

    # Aplicación de filtros dinámicos
    if filtro_estado:
        tareas = tareas.filter(estado=filtro_estado)
    
    if filtro_prioridad:
        tareas = tareas.filter(prioridad=filtro_prioridad)
    
    if busqueda:
        tareas = tareas.filter(
            Q(titulo__icontains=busqueda) |
            Q(descripcion__icontains=busqueda)
        )
    
    # Lógica de ordenamiento
    if filtro_orden == 'prioridad':
        orden_prioridad = {'urgente': 1, 'alta': 2, 'media': 3, 'baja': 4}
        # Nota: sorted() se usa para ordenamiento complejo que no es directo en base de datos
        tareas = sorted(tareas, key=lambda t: orden_prioridad.get(t.prioridad, 99))
    elif filtro_orden == 'vencimiento':
        tareas = tareas.order_by('fecha_vencimiento')
    elif filtro_orden == 'antiguo':
        tareas = tareas.order_by('creado_en')
    else:
        # Por defecto se muestran las más recientes primero
        if isinstance(tareas, list):
            pass # Ya está ordenado por la lógica de sorted o requiere reconversión si fuera necesario
        else:
            tareas = tareas.order_by('-creado_en')
    
    # Cálculo de métricas para los indicadores de la vista
    contadores = {
        'pendiente': Tarea.objects.filter(estado='pendiente').count() if user.rol == 'admin' else tareas.filter(estado='pendiente').count(),
        'en_progreso': Tarea.objects.filter(estado='en_progreso').count() if user.rol == 'admin' else tareas.filter(estado='en_progreso').count(),
        'en_revision': Tarea.objects.filter(estado='en_revision').count() if user.rol == 'admin' else tareas.filter(estado='en_revision').count(),
        'completado': Tarea.objects.filter(estado='completado').count() if user.rol == 'admin' else tareas.filter(estado='completado').count(),
        'total': len(tareas) if isinstance(tareas, list) else tareas.count(),
        'vencidas': (Tarea.objects.filter(fecha_vencimiento__lt=timezone.now().date()).exclude(estado='completado').count() 
                     if user.rol == 'admin' else 
                     sum(1 for t in tareas if t.esta_vencida())),
    }
    
    context = {
        'tareas': tareas,
        'puede_crear': user.rol in ['admin', 'manager'],
        'filtro_estado': filtro_estado,
        'filtro_prioridad': filtro_prioridad,
        'filtro_orden': filtro_orden,
        'busqueda': busqueda,
        'estados': Tarea.ESTADOS,
        'prioridades': Tarea.PRIORIDADES,
        'contadores': contadores,
    }
    return render(request, 'tareas/lista.html', context)

@login_required
@admin_o_manager
def tarea_crear(request):
    """
    Permite la creación de nuevas tareas. 
    Solo los administradores y managers tienen permiso para esta acción.
    Registra automáticamente el evento en el historial tras el guardado.
    """
    if request.method == 'POST':
        form = TareaForm(request.POST, user=request.user)
        if form.is_valid():
            tarea = form.save(commit=False)
            tarea.creador = request.user
            tarea.save()
            
            # Registro en el historial del sistema
            registrar_creacion(tarea, request.user)
            
            messages.success(request, f'✅ Tarea "{tarea.titulo}" creada exitosamente.')
            return redirect('tarea_detalle', pk=tarea.pk)
    else:
        form = TareaForm(user=request.user)
    
    return render(request, 'tareas/form.html', {
        'form': form,
        'titulo': 'Crear Tarea'
    })

@login_required
def tarea_detalle(request, pk):
    """
    Muestra la información detallada de una tarea, incluyendo comentarios e historial de cambios.
    Verifica que el usuario tenga permisos de observación antes de renderizar.
    """
    tarea = get_object_or_404(Tarea, pk=pk)
    
    # Validación de seguridad a nivel de objeto
    if not VerificarPermiso.puede_ver_tarea(request.user, tarea):
        messages.error(request, '❌ No tienes acceso a esta tarea.')
        return redirect('tarea_lista')
    
    historial_cambios = HistorialTarea.objects.filter(tarea=tarea).order_by('-creado_en')
    comentarios = tarea.comentarios.all()
    
    # Gestión de nuevos comentarios
    if request.method == 'POST':
        form_comentario = ComentarioForm(request.POST)
        if form_comentario.is_valid():
            comentario = form_comentario.save(commit=False)
            comentario.tarea = tarea
            comentario.usuario = request.user
            comentario.save()
            
            # Registro del comentario en el historial de la tarea
            registrar_comentario(tarea, request.user)
            
            messages.success(request, '💬 Comentario agregado.')
            return redirect('tarea_detalle', pk=tarea.pk)
    else:
        form_comentario = ComentarioForm()

    context = {
        'tarea': tarea,
        'comentarios': comentarios,
        'form_comentario': form_comentario,
        'puede_editar': VerificarPermiso.puede_gestionar_tarea(request.user, tarea),
        'puede_eliminar': VerificarPermiso.puede_eliminar_tarea(request.user, tarea),
        'puede_cambiar_estado': VerificarPermiso.puede_gestionar_tarea(request.user, tarea),
        'estados': Tarea.ESTADOS,
        'historial': historial_cambios,
    }
    return render(request, 'tareas/detalle.html', context)

@login_required
def tarea_editar(request, pk):
    """
    Gestiona la edición de campos de una tarea.
    Detecta cambios específicos en prioridad y responsable para generar registros detallados en el historial.
    """
    tarea = get_object_or_404(Tarea, pk=pk)
    
    if not VerificarPermiso.puede_gestionar_tarea(request.user, tarea):
        messages.error(request, '❌ No tienes permiso para editar esta tarea.')
        return redirect('tarea_detalle', pk=pk)
    
    if request.method == 'POST':
        # Captura de valores previos para auditoría
        prioridad_anterior = tarea.prioridad
        responsable_anterior = tarea.responsable
        
        form = TareaForm(request.POST, instance=tarea, user=request.user)
        if form.is_valid():
            tarea_actualizada = form.save()
            
            # Auditoría de cambio de prioridad
            if prioridad_anterior != tarea_actualizada.prioridad:
                registrar_cambio_priority(
                    tarea_actualizada, request.user,
                    prioridad_anterior, tarea_actualizada.prioridad
                )
            
            # Auditoría de cambio de responsable
            if responsable_anterior != tarea_actualizada.responsable:
                registrar_cambio_responsable(
                    tarea_actualizada, request.user,
                    responsable_anterior, tarea_actualizada.responsable
                )
            
            # Registro de edición general
            registrar_edicion(tarea_actualizada, request.user)
            
            messages.success(request, f'✅ Tarea "{tarea.titulo}" actualizada.')
            return redirect('tarea_detalle', pk=tarea.pk)
    else:
        form = TareaForm(instance=tarea, user=request.user)
    
    return render(request, 'tareas/form.html', {
        'form': form,
        'titulo': 'Editar Tarea',
        'tarea': tarea
    })

@login_required
def tarea_eliminar(request, pk):
    """
    Elimina permanentemente una tarea.
    Solo accesible para administradores y managers responsables del proyecto.
    """
    tarea = get_object_or_404(Tarea, pk=pk)
    
    if not VerificarPermiso.puede_eliminar_tarea(request.user, tarea):
        messages.error(request, '❌ No tienes permiso para eliminar tareas.')
        return redirect('tarea_detalle', pk=pk)
    
    if request.method == 'POST':
        titulo = tarea.titulo
        tarea.delete()
        messages.success(request, f'✅ Tarea "{titulo}" eliminada.')
        return redirect('tarea_lista')
    
    return render(request, 'tareas/eliminar.html', {'tarea': tarea})

@login_required
def tarea_cambiar_estado(request, pk):
    """
    Actualiza específicamente el estado de una tarea.
    Calcula automáticamente la fecha de completado si el nuevo estado es final.
    """
    tarea = get_object_or_404(Tarea, pk=pk)
    
    if not VerificarPermiso.puede_gestionar_tarea(request.user, tarea):
        messages.error(request, '❌ No tienes permiso para cambiar el estado.')
        return redirect('tarea_detalle', pk=pk)
    
    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')
        if nuevo_estado in dict(Tarea.ESTADOS):
            estado_anterior = tarea.estado
            
            tarea.estado = nuevo_estado
            if nuevo_estado == 'completado':
                tarea.fecha_completado = timezone.now()
            tarea.save()
            
            # Registro detallado del cambio de estado en el historial
            registrar_cambio_estado(
                tarea, request.user,
                estado_anterior, nuevo_estado
            )
            
            messages.success(request, f'✅ Estado actualizado a: {tarea.get_estado_display()}')
    
    return redirect('tarea_detalle', pk=pk)