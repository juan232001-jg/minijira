"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# config/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Importar vistas
from usuarios.views import login_view, registro_view, logout_view, perfil_view, perfil_editar_view
from core.views import dashboard
from usuarios.views_admin import admin_usuarios, cambiar_rol_usuario, toggle_usuario_activo

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # ===== AUTENTICACIÓN =====
    path('', login_view, name='login'),  # Página de inicio
    path('login/', login_view, name='login'),
    path('registro/', registro_view, name='registro'),
    path('logout/', logout_view, name='logout'),
    
    # ===== PERFIL =====
    path('perfil/', perfil_view, name='perfil'),
    path('perfil/editar/', perfil_editar_view, name='perfil_editar'),
    
    # ===== DASHBOARD =====
    path('dashboard/', dashboard, name='dashboard'),
    
    # ===== APPS =====
    path('proyectos/', include('proyectos.urls')),
    path('tareas/', include('tareas.urls')),

    # ===== ADMIN DE USUARIOS =====
    path('admin-panel/usuarios/', admin_usuarios, name='admin_usuarios'),
    path('admin-panel/usuarios/<int:pk>/cambiar-rol/', cambiar_rol_usuario, name='cambiar_rol_usuario'),
    path('admin-panel/usuarios/<int:pk>/toggle-activo/', toggle_usuario_activo, name='toggle_usuario_activo'),
]

# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
