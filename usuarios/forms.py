"""
Formularios para la gestión de usuarios, incluyendo el inicio de sesión
y el registro de nuevos miembros con validaciones personalizadas.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm , PasswordChangeForm
from .models import Usuario

class LoginForm(AuthenticationForm):
    """
    Formulario personalizado para la autenticación de usuarios.
    Incluye un campo adicional 'remember_me' para gestionar la persistencia de la sesión.
    """
    
    username = forms.CharField(
        label='Usuario',
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingresa tu usuario',
            'autofocus': True
        })
    )
    
    password = forms.CharField(
        label='Contraseña',
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingresa tu contraseña',
            'autocomplete': 'current-password'
        })
    )
    
    # Opción para mantener al usuario conectado tras cerrar el navegador
    remember_me = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='Recordarme'
    )

class RegistroForm(UserCreationForm):
    """
    Formulario para el registro de nuevos usuarios en la plataforma.
    Extiende UserCreationForm para incluir campos adicionales como email, nombre, apellido y empresa.
    """
    
    email = forms.EmailField(
        required=True, 
        label='Correo Electrónico',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'correo@ejemplo.com'
        })
    )
    
    first_name = forms.CharField(
        required=True, 
        label='Nombre',
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Tu nombre'
        })
    )
    
    last_name = forms.CharField(
        required=True, 
        label='Apellido',
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Tu apellido'
        })
    )
    
    empresa = forms.CharField(
        required=False, 
        label='Empresa (opcional)',
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre de tu empresa'
        })
    )
    
    class Meta:
        """Configuración del modelo y campos asociados al formulario de registro."""
        model = Usuario
        fields = ('username', 'email', 'first_name', 'last_name', 'empresa', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Elige un nombre de usuario'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        """Inicializa el formulario personalizando estilos y textos de ayuda."""
        super().__init__(*args, **kwargs)
        
        # Configuración detallada de etiquetas y mensajes de ayuda
        self.fields['username'].label = 'Nombre de usuario'
        self.fields['username'].help_text = 'Requerido. 150 caracteres o menos. Solo letras, dígitos y @/./+/-/_'
        
        self.fields['password1'].label = 'Contraseña'
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Mínimo 8 caracteres'
        })
        self.fields['password1'].help_text = '''
            <ul class="small text-muted">
                <li>Mínimo 8 caracteres</li>
                <li>No puede ser muy común</li>
                <li>No puede ser solo numérica</li>
            </ul>
        '''
        
        self.fields['password2'].label = 'Confirmar contraseña'
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Repite tu contraseña'
        })
        self.fields['password2'].help_text = 'Ingresa la misma contraseña para verificación'
    
    def clean_email(self):
        """
        Validación personalizada para asegurar que el correo electrónico es único en el sistema.
        """
        email = self.cleaned_data.get('email')
        if Usuario.objects.filter(email=email).exists():
            raise forms.ValidationError('Este correo electrónico ya está registrado.')
        return email
    
    def save(self, commit=True):
        """
        Sobrescribe el método save para asignar valores adicionales
        al nuevo usuario, como el rol por defecto de 'miembro'.
        """
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.empresa = self.cleaned_data.get('empresa', '')
        user.rol = 'miembro'  # Asignación automática de rol inicial
        
        if commit:
            user.save()
        return user

class PerfilEditarForm(forms.ModelForm):
    """Formulario para editar el perfil del usuario"""
    
    class Meta:
        model = Usuario
        fields = ['first_name', 'last_name', 'email', 'telefono', 'empresa', 'foto']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apellido'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'correo@ejemplo.com'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+57 300 123 4567'
            }),
            'empresa': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de tu empresa'
            }),
            'foto': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
        }
        labels = {
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'email': 'Correo Electrónico',
            'telefono': 'Teléfono',
            'empresa': 'Empresa',
            'foto': 'Foto de Perfil',
        }


class CambiarPasswordForm(PasswordChangeForm):
    """Formulario para cambiar contraseña"""
    
    old_password = forms.CharField(
        label='Contraseña Actual',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Escribe tu contraseña actual'
        })
    )
    new_password1 = forms.CharField(
        label='Nueva Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Escribe tu nueva contraseña'
        })
    )
    new_password2 = forms.CharField(
        label='Confirmar Nueva Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirma tu nueva contraseña'
        })
    )