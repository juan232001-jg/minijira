# usuarios/views_admin.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Usuario
from .permisos import solo_admin

@solo_admin
def admin_usuarios(request):
    """Solo Admin puede gestionar usuarios"""
    
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
    """Admin puede cambiar el rol de cualquier usuario"""
    
    usuario = get_object_or_404(Usuario, pk=pk)
    
    if request.method == 'POST':
        nuevo_rol = request.POST.get('rol')
        
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
    """Admin puede activar/desactivar usuarios"""
    
    usuario = get_object_or_404(Usuario, pk=pk)
    
    # No permitir desactivarse a sí mismo
    if usuario == request.user:
        messages.error(request, '❌ No puedes desactivar tu propia cuenta.')
        return redirect('admin_usuarios')
    
    usuario.is_active = not usuario.is_active
    usuario.save()
    
    estado = 'activado' if usuario.is_active else 'desactivado'
    messages.success(request, f'✅ Usuario {usuario.username} {estado}.')
    
    return redirect('admin_usuarios')