# config/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from usuarios import views as usuarios_views

urlpatterns = [
    # ===== ADMIN DE DJANGO =====
    path('admin/', admin.site.urls),
    
    # ===== AUTENTICACIÓN =====
    path('', usuarios_views.login_view, name='login'),
    path('registro/', usuarios_views.registro_view, name='registro'),
    path('logout/', usuarios_views.logout_view, name='logout'),
    
    # ===== PERFIL DE USUARIO =====
    path('perfil/', usuarios_views.perfil_view, name='perfil'),
    path('perfil/editar/', usuarios_views.perfil_editar_view, name='perfil_editar'),
    path('perfil/cambiar-password/', usuarios_views.cambiar_password_view, name='cambiar_password'),
    
    # ===== MÓDULOS DEL SISTEMA =====
    path('dashboard/', include('core.urls')),
    path('proyectos/', include('proyectos.urls')),
    path('tareas/', include('tareas.urls')),
]

# Servir archivos estáticos y media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)