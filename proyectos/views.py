"""
Vistas para la gestión de proyectos.
Implementa el CRUD de proyectos con restricciones de acceso basadas en roles
y visualización detallada incluyendo métricas de progreso de tareas.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Proyecto
from .forms import ProyectoForm
from usuarios.permisos import (
    admin_o_manager,
    todos_los_roles,
    VerificarPermiso
)

@login_required
@todos_los_roles
def proyecto_lista(request):
    """
    Despliega el listado de proyectos accesibles para el usuario actual.
    - Admin: Visualiza la totalidad de los proyectos del sistema.
    - Manager: Visualiza únicamente los proyectos bajo su autoría.
    - Miembro: Visualiza los proyectos en los que ha sido asignado como participante.
    """
    user = request.user
    
    # Filtrado dinámico según el nivel de privilegios y participación
    if user.rol == 'admin':
        proyectos = Proyecto.objects.all().order_by('-creado_en')
    elif user.rol == 'manager':
        proyectos = Proyecto.objects.filter(creador=user).order_by('-creado_en')
    else:
        proyectos = Proyecto.objects.filter(miembros=user).order_by('-creado_en')
    
    context = {
        'proyectos': proyectos,
        'puede_crear': user.rol in ['admin', 'manager'],
    }
    return render(request, 'proyectos/lista.html', context)

@login_required
@admin_o_manager
def proyecto_crear(request):
    """
    Gestiona la creación de nuevos proyectos.
    Asigna automáticamente al usuario actual como creador y primer miembro del equipo.
    """
    if request.method == 'POST':
        form = ProyectoForm(request.POST)
        if form.is_valid():
            proyecto = form.save(commit=False)
            proyecto.creador = request.user
            proyecto.save()
            
            # El creador se añade automáticamente a la lista de miembros
            proyecto.miembros.add(request.user)
            form.save_m2m() # Necesario para procesar el campo ManyToMany
            
            messages.success(request, f'✅ Proyecto "{proyecto.nombre}" creado exitosamente.')
            return redirect('proyecto_lista')
    else:
        form = ProyectoForm(user=request.user)
    
    return render(request, 'proyectos/form.html', {
        'form': form, 
        'titulo': 'Crear Proyecto'
    })

@login_required
@todos_los_roles
def proyecto_detalle(request, pk):
    """
    Muestra la información detallada de un proyecto, incluyendo sus tareas asociadas
    y estadísticas de cumplimiento actualizadas.
    """
    proyecto = get_object_or_404(Proyecto, pk=pk)

    # Verificación de permisos de visibilidad antes de cargar datos sensibles
    if not VerificarPermiso.puede_ver_proyecto(request.user, proyecto):
        messages.error(request, '❌ No tienes acceso a este proyecto.')
        return redirect('proyecto_lista')

    tareas = proyecto.tareas.all().order_by('-creado_en')

    # Métricas de estado de las tareas para indicadores visuales
    contadores = {
        'pendiente': tareas.filter(estado='pendiente').count(),
        'en_progreso': tareas.filter(estado='en_progreso').count(),
        'en_revision': tareas.filter(estado='en_revision').count(),
        'completado': tareas.filter(estado='completado').count(),
    }

    context = {
        'proyecto': proyecto,
        'tareas': tareas,
        'contadores': contadores,
        'puede_editar': VerificarPermiso.puede_gestionar_proyecto(request.user, proyecto),
        'puede_eliminar': request.user.rol == 'admin' or (
            request.user.rol == 'manager' and proyecto.creador == request.user
        ),
        'puede_crear_tarea': request.user.rol in ['admin', 'manager'],
    }
    return render(request, 'proyectos/detalle.html', context)

@login_required
def proyecto_editar(request, pk):
    """
    Permite la actualización de los metadatos y la composición del equipo de un proyecto.
    Válido para administradores o para el manager creador del mismo.
    """
    proyecto = get_object_or_404(Proyecto, pk=pk)
    
    if not VerificarPermiso.puede_gestionar_proyecto(request.user, proyecto):
        messages.error(request, '❌ No tienes permiso para editar este proyecto.')
        return redirect('proyecto_detalle', pk=pk)
    
    if request.method == 'POST':
        form = ProyectoForm(request.POST, instance=proyecto, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, f'✅ Proyecto "{proyecto.nombre}" actualizado.')
            return redirect('proyecto_detalle', pk=proyecto.pk)
    else:
        form = ProyectoForm(instance=proyecto, user=request.user)
    
    return render(request, 'proyectos/form.html', {
        'form': form,
        'titulo': 'Editar Proyecto',
        'proyecto': proyecto
    })

@login_required
def proyecto_eliminar(request, pk):
    """
    Finaliza y elimina permanentemente un proyecto y todas sus dependencias.
    Requiere confirmación previa por parte del usuario autorizado.
    """
    proyecto = get_object_or_404(Proyecto, pk=pk)
    
    if not VerificarPermiso.puede_gestionar_proyecto(request.user, proyecto):
        messages.error(request, '❌ No tienes permiso para eliminar este proyecto.')
        return redirect('proyecto_detalle', pk=pk)
    
    if request.method == 'POST':
        nombre = proyecto.nombre
        proyecto.delete()
        messages.success(request, f'✅ Proyecto "{nombre}" eliminado.')
        return redirect('proyecto_lista')
    
    return render(request, 'proyectos/eliminar.html', {'proyecto': proyecto})