# usuarios/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Usuario

class LoginForm(AuthenticationForm):
    """Formulario de login personalizado"""
    
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
    
    remember_me = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='Recordarme'
    )

class RegistroForm(UserCreationForm):
    """Formulario de registro personalizado"""
    
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
        model = Usuario
        fields = ('username', 'email', 'first_name', 'last_name', 'empresa', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Elige un nombre de usuario'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Personalizar labels y help text
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
        """Validar que el email no esté registrado"""
        email = self.cleaned_data.get('email')
        if Usuario.objects.filter(email=email).exists():
            raise forms.ValidationError('Este correo electrónico ya está registrado.')
        return email
    
    def save(self, commit=True):
        """Guardar usuario con rol por defecto"""
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.empresa = self.cleaned_data.get('empresa', '')
        user.rol = 'miembro'  # Rol por defecto
        
        if commit:
            user.save()
        return user