# usuarios/views.py

"""
Vistas para la gestión de usuarios, incluyendo autenticación (login/logout),
registro y gestión de perfiles.
"""

from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from .forms import RegistroForm, LoginForm, PerfilEditarForm, CambiarPasswordForm
from .models import Usuario
from proyectos.models import Proyecto
from tareas.models import Tarea
from historial.models import HistorialTarea
from usuarios.permisos import solo_admin


def login_view(request):
    """
    Gestiona el inicio de sesión de los usuarios.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            remember_me = form.cleaned_data.get('remember_me')
            
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                
                if not remember_me:
                    request.session.set_expiry(0)
                else:
                    request.session.set_expiry(2592000)
                
                messages.success(request, f'¡Bienvenido de nuevo, {user.get_full_name() or user.username}!')
                
                next_url = request.GET.get('next', 'dashboard')
                return redirect(next_url)
            else:
                messages.error(request, 'Usuario o contraseña incorrectos.')
        else:
            messages.error(request, 'Por favor corrige los errores del formulario.')
    else:
        form = LoginForm()
    
    return render(request, 'registration/login.html', {'form': form})

def registro_view(request):
    """
    Procesa el registro de nuevos usuarios en el sistema.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        
        if form.is_valid():
            user = form.save()
            
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'¡Cuenta creada exitosamente! Bienvenido, {user.get_full_name()}.')
                return redirect('dashboard')
        else:
            messages.error(request, 'Por favor corrige los errores del formulario.')
    else:
        form = RegistroForm()
    
    return render(request, 'registration/registro.html', {'form': form})


@login_required
def logout_view(request):
    """
    Finaliza la sesión actual del usuario.
    """
    username = request.user.username
    logout(request)
    messages.success(request, f'¡Hasta pronto, {username}!')
    return redirect('login')


@login_required
def perfil_view(request):
    """Vista del perfil del usuario con estadísticas completas"""
    
    user = request.user
    
    # ===== ESTADÍSTICAS DE PROYECTOS =====
    if user.rol == 'admin':
        proyectos = Proyecto.objects.all()
        tareas_base = Tarea.objects.all()
    elif user.rol == 'manager':
        proyectos = Proyecto.objects.filter(creador=user)
        tareas_base = Tarea.objects.filter(proyecto__creador=user)
    else:
        proyectos = Proyecto.objects.filter(miembros=user)
        tareas_base = Tarea.objects.filter(proyecto__miembros=user)
    
    # ===== CONTADORES DE TAREAS =====
    estadisticas_tareas = {
        'total': tareas_base.count(),
        'pendiente': tareas_base.filter(estado='pendiente').count(),
        'en_progreso': tareas_base.filter(estado='en_progreso').count(),
        'en_revision': tareas_base.filter(estado='en_revision').count(),
        'completado': tareas_base.filter(estado='completado').count(),
        'vencidas': tareas_base.filter(
            fecha_vencimiento__lt=timezone.now().date()
        ).exclude(estado='completado').count(),
    }
    
    # ===== TAREAS ASIGNADAS A MÍ =====
    mis_tareas = tareas_base.filter(responsable=user).count()
    
    # ===== PRODUCTIVIDAD MENSUAL (últimos 30 días) =====
    hace_30_dias = timezone.now() - timedelta(days=30)
    tareas_mes = tareas_base.filter(
        estado='completado',
        fecha_completado__gte=hace_30_dias
    ).count()
    
    # ===== PRODUCTIVIDAD POR DÍA (últimos 7 días) =====
    productividad_semanal = []
    labels_dias = []
    
    for i in range(6, -1, -1):
        dia = timezone.now().date() - timedelta(days=i)
        cantidad = tareas_base.filter(
            estado='completado',
            fecha_completado__date=dia
        ).count()
        productividad_semanal.append(cantidad)
        labels_dias.append(dia.strftime('%d/%m'))
    
    # ===== ACTIVIDAD RECIENTE =====
    actividad_reciente = HistorialTarea.objects.filter(
        usuario=user
    ).select_related('tarea').order_by('-creado_en')[:10]
    
    # ===== TAREAS RECIENTES ASIGNADAS =====
    tareas_recientes = tareas_base.filter(
        responsable=user
    ).order_by('-creado_en')[:5]
    
    context = {
        'usuario': user,
        'proyectos_count': proyectos.count(),
        'estadisticas_tareas': estadisticas_tareas,
        'mis_tareas': mis_tareas,
        'tareas_mes': tareas_mes,
        'actividad_reciente': actividad_reciente,
        'tareas_recientes': tareas_recientes,
        # Datos para gráfica
        'chart_productividad': productividad_semanal,
        'chart_labels': labels_dias,
    }
    
    return render(request, 'usuarios/perfil.html', context)


@login_required
def perfil_editar_view(request):
    """Editar información del perfil"""
    
    if request.method == 'POST':
        form = PerfilEditarForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Perfil actualizado correctamente.')
            return redirect('perfil')
    else:
        form = PerfilEditarForm(instance=request.user)
    
    return render(request, 'usuarios/perfil_editar.html', {
        'form': form
    })


@login_required
def cambiar_password_view(request):
    """Cambiar contraseña del usuario"""
    
    if request.method == 'POST':
        form = CambiarPasswordForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, '✅ Contraseña cambiada correctamente.')
            return redirect('perfil')
    else:
        form = CambiarPasswordForm(user=request.user)
    
    return render(request, 'usuarios/cambiar_password.html', {
        'form': form
    })



@login_required
@solo_admin
def admin_usuarios(request):
    """Panel de administración de usuarios - Solo Admin"""
    
    usuarios = Usuario.objects.all().order_by('rol', 'username')
    
    # Contadores por rol
    contadores = {
        'total': usuarios.count(),
        'admins': usuarios.filter(rol='admin').count(),
        'managers': usuarios.filter(rol='manager').count(),
        'miembros': usuarios.filter(rol='miembro').count(),
        'activos': usuarios.filter(is_active=True).count(),
        'inactivos': usuarios.filter(is_active=False).count(),
    }
    
    context = {
        'usuarios': usuarios,
        'contadores': contadores,
    }
    return render(request, 'usuarios/admin_usuarios.html', context)


@login_required
@solo_admin
def cambiar_rol_usuario(request, pk):
    """Cambiar rol de un usuario - Solo Admin"""
    
    usuario = get_object_or_404(Usuario, pk=pk)
    
    if request.method == 'POST':
        nuevo_rol = request.POST.get('rol')
        if nuevo_rol in ['admin', 'manager', 'miembro']:
            rol_anterior = usuario.rol
            usuario.rol = nuevo_rol
            usuario.save()
            messages.success(
                request,
                f'✅ Rol de {usuario.get_full_name()} cambiado de {rol_anterior} a {nuevo_rol}.'
            )
        else:
            messages.error(request, '❌ Rol no válido.')
    
    return redirect('admin_usuarios')


@login_required
@solo_admin
def toggle_usuario_activo(request, pk):
    """Activar/Desactivar un usuario - Solo Admin"""
    
    usuario = get_object_or_404(Usuario, pk=pk)
    
    # No permitir desactivar al propio admin
    if usuario == request.user:
        messages.error(request, '❌ No puedes desactivar tu propia cuenta.')
        return redirect('admin_usuarios')
    
    if request.method == 'POST':
        usuario.is_active = not usuario.is_active
        usuario.save()
        
        estado = 'activado' if usuario.is_active else 'desactivado'
        messages.success(
            request,
            f'✅ Usuario {usuario.get_full_name()} {estado} correctamente.'
        )
    
    return redirect('admin_usuarios')