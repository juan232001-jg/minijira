"""
Vistas principales del núcleo del sistema.
Contiene la lógica central del dashboard, incluyendo la recopilación de métricas,
estadísticas por rol y preparación de datos para visualizaciones gráficas.
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from proyectos.models import Proyecto
from tareas.models import Tarea

@login_required
def dashboard(request):

    """
    Controlador principal del tablero de mandos (Dashboard).
    
    Centraliza la información relevante para el usuario según su nivel de acceso.
    Calcula indicadores de estado, prioridad, productividad semanal y proyectos activos.
    """
    user = request.user

    # Segmentación de datos base según el rol de seguridad del usuario
    if user.rol == 'admin':
        # El administrador posee visibilidad global de todo el ecosistema
        tareas_base = Tarea.objects.all()
        proyectos = Proyecto.objects.all()
    elif user.rol == 'manager':
        # El manager visualiza únicamente el entorno de sus propios proyectos
        tareas_base = Tarea.objects.filter(proyecto__creador=user)
        proyectos = Proyecto.objects.filter(creador=user)
    else:
        # El miembro estándar visualiza sus asignaciones y proyectos de participación
        tareas_base = Tarea.objects.filter(proyecto__miembros=user)
        proyectos = Proyecto.objects.filter(miembros=user)

    # Cálculo de métricas cuantitativas por estado de tarea
    contadores = {
        'pendiente': tareas_base.filter(estado='pendiente').count(),
        'en_progreso': tareas_base.filter(estado='en_progreso').count(),
        'en_revision': tareas_base.filter(estado='en_revision').count(),
        'completado': tareas_base.filter(estado='completado').count(),
        'vencidas': tareas_base.filter(
            fecha_vencimiento__lt=timezone.now().date()
        ).exclude(estado='completado').count(),
        'total': tareas_base.count(),
    }

    # Distribución de tareas según su nivel de urgencia/prioridad
    prioridades = {
        'urgente': tareas_base.filter(prioridad='urgente').count(),
        'alta': tareas_base.filter(prioridad='alta').count(),
        'media': tareas_base.filter(prioridad='media').count(),
        'baja': tareas_base.filter(prioridad='baja').count(),
    }

    # Preparación de datos históricos de productividad (última semana)
    # Se utiliza para alimentar la gráfica de tendencia de tareas finalizadas
    ultimos_7_dias = []
    labels_dias = []
    for i in range(6, -1, -1):
        dia = timezone.now().date() - timedelta(days=i)
        cantidad = tareas_base.filter(
            estado='completado',
            fecha_completado__date=dia
        ).count()
        ultimos_7_dias.append(cantidad)
        labels_dias.append(dia.strftime('%d/%m'))

    # Selección de proyectos destacados (activos y recientes)
    proyectos_activos = proyectos.filter(
        estado='activo'
    ).order_by('-creado_en')[:5]

    # Feed de actividad reciente de tareas
    tareas_recientes = tareas_base.order_by('-creado_en')[:8]

    # Consolidación del contexto para el renderizado de la plantilla
    context = {
        'contadores': contadores,
        'prioridades': prioridades,
        'proyectos_activos': proyectos_activos,
        'tareas_recientes': tareas_recientes,
        'proyectos_count': proyectos.filter(estado='activo').count(),
        
        # Estructuración de datos para la librería Chart.js
        'chart_estados': [
            contadores['pendiente'],
            contadores['en_progreso'],
            contadores['en_revision'],
            contadores['completado'],
        ],
        'chart_prioridades': [
            prioridades['urgente'],
            prioridades['alta'],
            prioridades['media'],
            prioridades['baja'],
        ],
        'chart_dias': ultimos_7_dias,
        'chart_labels_dias': labels_dias,
    }

    return render(request, 'dashboard.html', context)

@login_required
def calendario(request):
    """
    Controlador del calendario de eventos.
    
    Muestra un calendario interactivo con eventos programados.
    """
    return render(request, 'calendario.html')

@login_required
def calendario_eventos(request):
    """
    Retorna las tareas en formato JSON para FullCalendar
    Solo tareas con fecha de vencimiento
    """
    user = request.user

    # Filtrar tareas según rol
    if user.rol == 'admin':
        tareas = Tarea.objects.all()
    elif user.rol == 'manager':
        tareas = Tarea.objects.filter(proyecto__creador=user)
    else:
        tareas = Tarea.objects.filter(proyecto__miembros=user)

    # Filtro opcional: solo mis tareas
    solo_mis_tareas = request.GET.get('mis_tareas', 'false') == 'true'
    if solo_mis_tareas:
        tareas = tareas.filter(responsable=user)

    # Solo tareas con fecha de vencimiento
    tareas = tareas.filter(
        fecha_vencimiento__isnull=False
    ).select_related('proyecto', 'responsable')

    # Colores por prioridad
    colores_prioridad = {
        'urgente': '#dc3545',  # Rojo
        'alta':    '#fd7e14',  # Naranja
        'media':   '#0d6efd',  # Azul
        'baja':    '#198754',  # Verde
    }

    # Colores de borde por estado
    bordes_estado = {
        'pendiente':   '#ffc107',  # Amarillo
        'en_progreso': '#0d6efd',  # Azul
        'en_revision': '#0dcaf0',  # Cyan
        'completado':  '#198754',  # Verde
    }

    # Construir eventos para FullCalendar
    eventos = []
    for tarea in tareas:
        # Determinar si está vencida
        esta_vencida = (
            tarea.fecha_vencimiento < timezone.now().date() and
            tarea.estado != 'completado'
        )

        color = '#6c757d' if esta_vencida else colores_prioridad.get(tarea.prioridad, '#0d6efd')

        eventos.append({
            'id': tarea.pk,
            'title': tarea.titulo,
            'start': tarea.fecha_vencimiento.isoformat(),
            'url': f'/tareas/{tarea.pk}/',
            'backgroundColor': color,
            'borderColor': bordes_estado.get(tarea.estado, '#0d6efd'),
            'textColor': '#ffffff',
            'extendedProps': {
                'proyecto': tarea.proyecto.nombre,
                'responsable': tarea.responsable.get_full_name() if tarea.responsable else 'Sin asignar',
                'prioridad': tarea.get_prioridad_display() if hasattr(tarea, 'get_prioridad_display') else tarea.prioridad,
                'estado': tarea.get_estado_display() if hasattr(tarea, 'get_estado_display') else tarea.estado,
                'vencida': esta_vencida,
            }
        })

    return JsonResponse(eventos, safe=False)