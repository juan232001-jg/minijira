"""
Configuración de rutas para la aplicación de Tareas.
Define los puntos de entrada para el listado, creación, detalle, edición y gestión de estados de tareas.
"""

from django.urls import path
from . import views

urlpatterns = [
    # Listado general de tareas
    path('', views.tarea_lista, name='tarea_lista'),
    
    # Creación de nuevas tareas
    path('crear/', views.tarea_crear, name='tarea_crear'),
    
    # Vista de detalle de una tarea específica
    path('<int:pk>/', views.tarea_detalle, name='tarea_detalle'),
    
    # Edición de información de una tarea
    path('<int:pk>/editar/', views.tarea_editar, name='tarea_editar'),
    
    # Eliminación de una tarea
    path('<int:pk>/eliminar/', views.tarea_eliminar, name='tarea_eliminar'),
    
    # Acción específica para el cambio rápido de estado
    path('<int:pk>/cambiar-estado/', views.tarea_cambiar_estado, name='tarea_cambiar_estado'),
]