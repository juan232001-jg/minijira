# tareas/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Tarea
from .forms import TareaForm, ComentarioForm
from comentarios.models import Comentario
from usuarios.permisos import VerificarPermiso, admin_o_manager

@login_required
def tarea_lista(request):
    """
    Lista tareas según el rol:
    - Admin: VE TODAS las tareas
    - Manager: VE tareas de sus proyectos
    - Miembro: VE solo sus tareas asignadas
    """
    user = request.user
    
    if user.rol == 'admin':
        tareas = Tarea.objects.all().order_by('-creado_en')
    elif user.rol == 'manager':
        tareas = Tarea.objects.filter(
            proyecto__creador=user
        ).order_by('-creado_en')
    else:
        # Miembro ve solo tareas de proyectos donde participa
        tareas = Tarea.objects.filter(
            proyecto__miembros=user
        ).order_by('-creado_en')
    
    context = {
        'tareas': tareas,
        'puede_crear': user.rol in ['admin', 'manager'],
    }
    return render(request, 'tareas/lista.html', context)


@login_required
@admin_o_manager
def tarea_crear(request):
    """Solo Admin y Manager pueden crear tareas"""
    
    if request.method == 'POST':
        form = TareaForm(request.POST, user=request.user)
        if form.is_valid():
            tarea = form.save(commit=False)
            tarea.creador = request.user
            tarea.save()
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
    Ver detalle de una tarea
    Todos pueden ver si tienen acceso al proyecto
    """
    tarea = get_object_or_404(Tarea, pk=pk)
    
    # Verificar que puede ver la tarea
    if not VerificarPermiso.puede_ver_tarea(request.user, tarea):
        messages.error(request, '❌ No tienes acceso a esta tarea.')
        return redirect('tarea_lista')
    
    comentarios = tarea.comentarios.all()
    
    # Todos pueden comentar si pueden ver la tarea
    if request.method == 'POST':
        form_comentario = ComentarioForm(request.POST)
        if form_comentario.is_valid():
            comentario = form_comentario.save(commit=False)
            comentario.tarea = tarea
            comentario.usuario = request.user
            comentario.save()
            messages.success(request, '💬 Comentario agregado.')
            return redirect('tarea_detalle', pk=tarea.pk)
    else:
        form_comentario = ComentarioForm()
    
    context = {
        'tarea': tarea,
        'comentarios': comentarios,
        'form_comentario': form_comentario,
        # Permisos para el template
        'puede_editar': VerificarPermiso.puede_gestionar_tarea(request.user, tarea),
        'puede_eliminar': VerificarPermiso.puede_eliminar_tarea(request.user, tarea),
        'puede_cambiar_estado': VerificarPermiso.puede_gestionar_tarea(request.user, tarea),
    }
    return render(request, 'tareas/detalle.html', context)


@login_required
def tarea_editar(request, pk):
    """
    Editar tarea:
    - Admin: puede editar cualquier tarea
    - Manager: solo tareas de sus proyectos
    - Miembro: solo sus tareas asignadas
    """
    tarea = get_object_or_404(Tarea, pk=pk)
    
    if not VerificarPermiso.puede_gestionar_tarea(request.user, tarea):
        messages.error(request, '❌ No tienes permiso para editar esta tarea.')
        return redirect('tarea_detalle', pk=pk)
    
    if request.method == 'POST':
        form = TareaForm(request.POST, instance=tarea, user=request.user)
        if form.is_valid():
            form.save()
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
    Eliminar tarea:
    - Admin: puede eliminar cualquier tarea
    - Manager: solo tareas de sus proyectos
    - Miembro: NUNCA puede eliminar
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
    Cambiar estado:
    - Admin: cualquier tarea
    - Manager: tareas de sus proyectos
    - Miembro: solo sus tareas asignadas
    """
    tarea = get_object_or_404(Tarea, pk=pk)
    
    if not VerificarPermiso.puede_gestionar_tarea(request.user, tarea):
        messages.error(request, '❌ No tienes permiso para cambiar el estado.')
        return redirect('tarea_detalle', pk=pk)
    
    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')
        if nuevo_estado in dict(Tarea.ESTADOS):
            tarea.estado = nuevo_estado
            if nuevo_estado == 'completado':
                tarea.fecha_completado = timezone.now()
            tarea.save()
            messages.success(request, f'✅ Estado cambiado a: {tarea.get_estado_display()}')
    
    return redirect('tarea_detalle', pk=pk)