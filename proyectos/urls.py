"""
Configuración de rutas para la gestión de proyectos.
Define los puntos de acceso para el listado global, creación, detalles y mantenimiento de proyectos.
"""

from django.urls import path
from . import views

urlpatterns = [
    # Visualización principal de los proyectos accesibles para el usuario
    path('', views.proyecto_lista, name='proyecto_lista'),
    
    # Formulario para el registro de nuevos proyectos
    path('crear/', views.proyecto_crear, name='proyecto_crear'),
    
    # Vista detallada de un proyecto, incluyendo sus tareas
    path('<int:pk>/', views.proyecto_detalle, name='proyecto_detalle'),
    
    # Formulario para la modificación de un proyecto existente
    path('<int:pk>/editar/', views.proyecto_editar, name='proyecto_editar'),
    
    # Proceso de confirmación y eliminación de un proyecto
    path('<int:pk>/eliminar/', views.proyecto_eliminar, name='proyecto_eliminar'),
]