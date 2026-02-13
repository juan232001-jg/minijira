
from django.urls import path
from . import views

urlpatterns = [
    path('', views.proyecto_lista, name='proyecto_lista'),
    path('crear/', views.proyecto_crear, name='proyecto_crear'),
    path('<int:pk>/', views.proyecto_detalle, name='proyecto_detalle'),
    path('<int:pk>/editar/', views.proyecto_editar, name='proyecto_editar'),
    path('<int:pk>/eliminar/', views.proyecto_eliminar, name='proyecto_eliminar'),
]