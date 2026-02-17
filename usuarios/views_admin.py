"""
Vistas administrativas para la gestión de usuarios.
Permite a los administradores listar usuarios, cambiar roles y gestionar el estado de activación.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Usuario
from .permisos import solo_admin

@solo_admin
def admin_usuarios(request):
    """
    Despliega un panel con el listado completo de usuarios y estadísticas básicas por rol.
    Acceso restringido únicamente a usuarios con rol de administrador.
    """
    
    usuarios = Usuario.objects.all().order_by('rol', 'username')
    
    context = {
        'usuarios': usuarios,
        'total_admins': usuarios.filter(rol='admin').count(),
        'total_managers': usuarios.filter(rol='manager').count(),
        'total_miembros': usuarios.filter(rol='miembro').count(),
    }
    return render(request, 'usuarios/admin_usuarios.html', context)

@solo_admin
def cambiar_rol_usuario(request, pk):
    """
    Permite a un administrador modificar el rol de un usuario específico.
    Valida que el nuevo rol se encuentre dentro de las opciones permitidas.
    """
    
    usuario = get_object_or_404(Usuario, pk=pk)
    
    if request.method == 'POST':
        nuevo_rol = request.POST.get('rol')
        
        # Validación de integridad para asegurar que el rol es válido
        if nuevo_rol in ['admin', 'manager', 'miembro']:
            rol_anterior = usuario.get_rol_display()
            usuario.rol = nuevo_rol
            usuario.save()
            messages.success(
                request,
                f'✅ Rol de {usuario.username} cambiado de {rol_anterior} a {usuario.get_rol_display()}'
            )
        else:
            messages.error(request, '❌ Rol inválido.')
    
    return redirect('admin_usuarios')

@solo_admin
def toggle_usuario_activo(request, pk):
    """
    Alterna el estado de activación (`is_active`) de un usuario.
    Incluye una restricción de seguridad para evitar que un administrador se desactive a sí mismo.
    """
    
    usuario = get_object_or_404(Usuario, pk=pk)
    
    # Verificación de seguridad preventia
    if usuario == request.user:
        messages.error(request, '❌ No puedes desactivar tu propia cuenta.')
        return redirect('admin_usuarios')
    
    # Inversión del estado booleano
    usuario.is_active = not usuario.is_active
    usuario.save()
    
    estado = 'activado' if usuario.is_active else 'desactivado'
    messages.success(request, f'✅ Usuario {usuario.username} {estado}.')
    
    return redirect('admin_usuarios')