# core/views.py

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from proyectos.models import Proyecto
from tareas.models import Tarea

@login_required
def dashboard(request):
    """Vista del dashboard principal"""
    
    # Obtener proyectos del usuario
    proyectos = Proyecto.objects.filter(
        miembros=request.user,
        estado='activo'
    ).order_by('-creado_en')[:5]
    
    # Obtener tareas del usuario
    tareas_recientes = Tarea.objects.filter(
        responsable=request.user
    ).order_by('-creado_en')[:10]
    
    # Estadísticas
    context = {
        'proyectos': proyectos,
        'tareas_recientes': tareas_recientes,
        'proyectos_activos': Proyecto.objects.filter(miembros=request.user, estado='activo').count(),
        'tareas_pendientes': Tarea.objects.filter(responsable=request.user, estado='pendiente').count(),
        'tareas_en_progreso': Tarea.objects.filter(responsable=request.user, estado='en_progreso').count(),
        'tareas_completadas': Tarea.objects.filter(responsable=request.user, estado='completado').count(),
    }
    
    return render(request, 'dashboard.html', context)