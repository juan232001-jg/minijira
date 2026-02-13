

from django.urls import path
from . import views

urlpatterns = [
    path('', views.tarea_lista, name='tarea_lista'),
    path('crear/', views.tarea_crear, name='tarea_crear'),
    path('<int:pk>/', views.tarea_detalle, name='tarea_detalle'),
    path('<int:pk>/editar/', views.tarea_editar, name='tarea_editar'),
    path('<int:pk>/eliminar/', views.tarea_eliminar, name='tarea_eliminar'),
    path('<int:pk>/cambiar-estado/', views.tarea_cambiar_estado, name='tarea_cambiar_estado'),
]