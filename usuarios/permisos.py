# usuarios/permisos.py

from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied

# DECORADORES DE ROLES


def solo_admin(view_func):
    """Solo el Administrador puede acceder"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.rol != 'admin':
            messages.error(request, '❌ No tienes permiso. Solo Administradores.')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper

def admin_o_manager(view_func):
    """Admin y Manager pueden acceder"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.rol not in ['admin', 'manager']:
            messages.error(request, '❌ No tienes permiso. Solo Managers y Administradores.')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper

def todos_los_roles(view_func):
    """Todos los roles autenticados pueden acceder"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper

# ============================================
# HELPERS DE VERIFICACIÓN
# ============================================

class VerificarPermiso:
    """
    Clase helper para verificar permisos
    en cualquier parte del código
    """
    
    @staticmethod
    def es_admin(user):
        """Verifica si el usuario es administrador"""
        return user.is_authenticated and user.rol == 'admin'
    
    @staticmethod
    def es_manager(user):
        """Verifica si el usuario es manager"""
        return user.is_authenticated and user.rol == 'manager'
    
    @staticmethod
    def es_miembro(user):
        """Verifica si el usuario es miembro"""
        return user.is_authenticated and user.rol == 'miembro'
    
    @staticmethod
    def puede_gestionar_proyecto(user, proyecto):
        """
        Verifica si puede crear/editar/eliminar un proyecto
        - Admin: siempre puede
        - Manager: solo sus proyectos
        - Miembro: nunca
        """
        if user.rol == 'admin':
            return True
        if user.rol == 'manager' and proyecto.creador == user:
            return True
        return False
    
    @staticmethod
    def puede_ver_proyecto(user, proyecto):
        """
        Verifica si puede ver un proyecto
        - Admin: todos los proyectos
        - Manager: sus proyectos
        - Miembro: proyectos donde es miembro
        """
        if user.rol == 'admin':
            return True
        if user.rol == 'manager' and proyecto.creador == user:
            return True
        if proyecto.miembros.filter(id=user.id).exists():
            return True
        return False
    
    @staticmethod
    def puede_gestionar_tarea(user, tarea):
        """
        Verifica si puede crear/editar una tarea
        - Admin: siempre puede
        - Manager: tareas de sus proyectos
        - Miembro: solo sus tareas asignadas
        """
        if user.rol == 'admin':
            return True
        if user.rol == 'manager' and tarea.proyecto.creador == user:
            return True
        if user.rol == 'miembro' and tarea.responsable == user:
            return True
        return False
    
    @staticmethod
    def puede_eliminar_tarea(user, tarea):
        """
        Solo Admin y Manager (dueño del proyecto) pueden eliminar
        - Miembro: NUNCA puede eliminar
        """
        if user.rol == 'admin':
            return True
        if user.rol == 'manager' and tarea.proyecto.creador == user:
            return True
        return False
    
    @staticmethod
    def puede_ver_tarea(user, tarea):
        """
        Verifica si puede ver una tarea
        - Admin: todas las tareas
        - Manager: tareas de sus proyectos
        - Miembro: tareas de proyectos donde participa
        """
        if user.rol == 'admin':
            return True
        if user.rol == 'manager' and tarea.proyecto.creador == user:
            return True
        if tarea.proyecto.miembros.filter(id=user.id).exists():
            return True
        return False
    
    @staticmethod
    def puede_gestionar_usuarios(user):
        """Solo Admin puede gestionar usuarios"""
        return user.rol == 'admin'
    
    @staticmethod
    def puede_ver_reportes(user):
        """Admin y Manager pueden ver reportes"""
        return user.rol in ['admin', 'manager']