"""
Definición de decoradores y clases de utilidad para la gestión de permisos en el sistema.
Permite controlar el acceso a vistas y acciones basado en los roles de usuario (Admin, Manager, Miembro).
"""

from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied

# ============================================
# DECORADORES DE ACCESO POR ROL
# ============================================

def solo_admin(view_func):
    """
    Restringe el acceso únicamente a usuarios con el rol de 'admin'.
    Si el usuario no está autenticado, redirige al login.
    Si el usuario no es admin, redirige al dashboard con un mensaje de error.
    """
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
    """
    Restringe el acceso únicamente a usuarios con rol de 'admin' o 'manager'.
    Sigue la misma lógica de redirección que 'solo_admin'.
    """
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
    """
    Asegura que el usuario esté autenticado para acceder a la vista,
    independientemente de su rol específico.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper

# ============================================
# CLASE DE VERIFICACIÓN DE PERMISOS (HELPERS)
# ============================================

class VerificarPermiso:
    """
    Provee métodos estáticos centralizados para validar permisos granulares
    sobre objetos específicos (proyectos, tareas, usuarios).
    """
    
    @staticmethod
    def es_admin(user):
        """Valida si el usuario tiene privilegios de administrador."""
        return user.is_authenticated and user.rol == 'admin'
    
    @staticmethod
    def es_manager(user):
        """Valida si el usuario tiene privilegios de manager."""
        return user.is_authenticated and user.rol == 'manager'
    
    @staticmethod
    def es_miembro(user):
        """Valida si el usuario es un miembro estándar del equipo."""
        return user.is_authenticated and user.rol == 'miembro'
    
    @staticmethod
    def puede_gestionar_proyecto(user, proyecto):
        """
        Determina si un usuario puede crear, editar o eliminar un proyecto.
        - Admin: Acceso total.
        - Manager: Solo si es el creador del proyecto.
        - Miembro: Sin permisos de gestión.
        """
        if user.rol == 'admin':
            return True
        if user.rol == 'manager' and proyecto.creador == user:
            return True
        return False
    
    @staticmethod
    def puede_ver_proyecto(user, proyecto):
        """
        Determina si un usuario puede visualizar un proyecto.
        - Admin: Acceso total.
        - Manager: Solo sus proyectos.
        - Miembro: Solo proyectos en los que participa.
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
        Determina si un usuario puede crear o editar una tarea específica.
        - Admin: Acceso total.
        - Manager: Solo tareas pertenecientes a sus proyectos.
        - Miembro: Solo si es el responsable de la tarea.
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
        Determina si un usuario tiene permisos para eliminar una tarea.
        Acceso restringido a Admins y Managers (dueños del proyecto).
        Los miembros nunca pueden eliminar tareas.
        """
        if user.rol == 'admin':
            return True
        if user.rol == 'manager' and tarea.proyecto.creador == user:
            return True
        return False
    
    @staticmethod
    def puede_ver_tarea(user, tarea):
        """
        Determina la visibilidad de una tarea.
        Basado en el acceso del usuario al proyecto contenedor de la tarea.
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
        """
        Verifica permisos para acceder al panel de administración de usuarios.
        Exclusivo para administradores.
        """
        return user.rol == 'admin'
    
    @staticmethod
    def puede_ver_reportes(user):
        """
        Verifica permisos para visualizar estadísticas y reportes globales.
        Accesible para administradores y managers.
        """
        return user.rol in ['admin', 'manager']