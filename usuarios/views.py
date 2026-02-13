# usuarios/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .forms import RegistroForm, LoginForm
from .models import Usuario

def login_view(request):
    """Vista de inicio de sesión"""
    
    # Si el usuario ya está autenticado, redirigir al dashboard
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            remember_me = form.cleaned_data.get('remember_me')
            
            # Autenticar usuario
            user = authenticate(username=username, password=password)
            
            if user is not None:
                # Login exitoso
                login(request, user)
                
                # Configurar duración de la sesión
                if not remember_me:
                    # Sesión expira al cerrar el navegador
                    request.session.set_expiry(0)
                else:
                    # Sesión dura 30 días
                    request.session.set_expiry(2592000)  # 30 días en segundos
                
                messages.success(request, f'¡Bienvenido de nuevo, {user.get_full_name() or user.username}!')
                
                # Redirigir a la página solicitada o al dashboard
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
    """Vista de registro de nuevos usuarios"""
    
    # Si el usuario ya está autenticado, redirigir al dashboard
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        
        if form.is_valid():
            # Crear usuario
            user = form.save()
            
            # Autenticar y hacer login automáticamente
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
    """Vista de cierre de sesión"""
    
    username = request.user.username
    logout(request)
    messages.success(request, f'¡Hasta pronto, {username}!')
    return redirect('login')

@login_required
def perfil_view(request):
    """Vista del perfil de usuario"""
    return render(request, 'usuarios/perfil.html')

@login_required
@require_http_methods(["GET", "POST"])
def perfil_editar_view(request):
    """Vista para editar perfil de usuario"""
    
    if request.method == 'POST':
        user = request.user
        
        # Actualizar datos
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.telefono = request.POST.get('telefono', '')
        user.empresa = request.POST.get('empresa', '')
        
        # Manejar foto de perfil
        if 'foto' in request.FILES:
            user.foto = request.FILES['foto']
        
        user.save()
        messages.success(request, 'Perfil actualizado exitosamente.')
        return redirect('perfil')
    
    return render(request, 'usuarios/perfil_editar.html')