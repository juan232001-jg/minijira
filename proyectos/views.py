# proyectos/views.py

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
    user = request.user
    
    if user.rol == 'admin':
        # Admin ve absolutamente todos
        proyectos = Proyecto.objects.all().order_by('-creado_en')
    elif user.rol == 'manager':
        # Manager ve solo los que creó
        proyectos = Proyecto.objects.filter(
            creador=user
        ).order_by('-creado_en')
    else:
        # Miembro ve solo donde es miembro
        proyectos = Proyecto.objects.filter(
            miembros=user
        ).order_by('-creado_en')
    
    context = {
        'proyectos': proyectos,
        'puede_crear': user.rol in ['admin', 'manager'],
    }
    return render(request, 'proyectos/lista.html', context)


@login_required
@admin_o_manager
def proyecto_crear(request):
    """Crear nuevo proyecto"""
    if request.method == 'POST':
        form = ProyectoForm(request.POST)
        if form.is_valid():
            proyecto = form.save(commit=False)
            proyecto.creador = request.user
            proyecto.save()
            proyecto.miembros.add(request.user)
            form.save_m2m()
            messages.success(request, '✅ Proyecto "{proyecto.nombre}" creado exitosamente.')
            return redirect('proyecto_lista')
    else:
        form = ProyectoForm(user=request.user)
    
    return render(request, 'proyectos/form.html', {'form': form , 'titulo': 'Crear Proyecto'})

@login_required
@todos_los_roles
def proyecto_detalle(request, pk):
    """Detalle de un proyecto"""
    proyecto = get_object_or_404(Proyecto, pk=pk)
    if not VerificarPermiso.puede_ver_proyecto(request.user, proyecto):
        messages.error(request, '❌ No tienes acceso a este proyecto.')
        return redirect('proyecto_lista')

    tareas = proyecto.tareas.all()
    context = {
        'proyecto': proyecto,
        'tareas': tareas,
        # Permisos para el template
        'puede_editar': VerificarPermiso.puede_gestionar_proyecto(request.user, proyecto),
        'puede_eliminar': request.user.rol == 'admin' or (
            request.user.rol == 'manager' and proyecto.creador == request.user
        ),
        'puede_crear_tarea': request.user.rol in ['admin', 'manager'],
    }
    return render(request, 'proyectos/detalle.html', context)

@login_required
def proyecto_editar(request, pk):
    """Editar proyecto"""
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
    """Eliminar proyecto"""
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