"""
Configuración global para el proyecto MiniJira.
Contiene las especificaciones de seguridad, aplicaciones instaladas, middleware,
bases de datos y configuraciones de internacionalización.
"""

from pathlib import Path

# Configuración de rutas base del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

# ===== CONFIGURACIÓN DE SEGURIDAD =====
# SECRET_KEY para firmas criptográficas (Debe mantenerse secreta en producción)
SECRET_KEY = 'django-insecure-554hch6i+_h&$am1s07)-&r1w^)+@4^93%!v@u6s=#u!)u*+0r'

# Modo depuración (Desactivar en entornos de producción)
DEBUG = True

ALLOWED_HOSTS = []

# ===== APLICACIONES DEL SISTEMA =====
INSTALLED_APPS = [
    # Aplicaciones nativas de Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Aplicaciones del proyecto (Lógica de negocio)
    'usuarios',
    'proyectos',
    'tareas',
    'comentarios',
    'historial',
    
    # Aplicaciones de terceros
    'crispy_forms',
    'crispy_bootstrap5',
]

# ===== MIDDLEWARE =====
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

# ===== PLANTILLAS (TEMPLATES) =====
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'], # Directorio global de plantillas
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# ===== BASE DE DATOS =====
# Configuración para PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'minijira',
        'USER': 'postgres',
        'PASSWORD': '12345',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# ===== VALIDACIÓN DE CONTRASEÑAS =====
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ===== INTERNACIONALIZACIÓN =====
LANGUAGE_CODE = 'es-co' # Configurado para español de Colombia/Latinoamérica

TIME_ZONE = 'America/Bogota'

USE_I18N = True

USE_TZ = True

# ===== ARCHIVOS ESTÁTICOS Y MEDIA =====
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ===== MODELO DE USUARIO PERSONALIZADO =====
# Indica a Django que utilice el modelo extendido de la app 'usuarios'
AUTH_USER_MODEL = 'usuarios.Usuario'

# ===== CONFIGURACIÓN DE RUTAS DE ACCESO =====
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'
LOGIN_URL = 'login'

# Gestión detallada de la duración de sesiones
SESSION_COOKIE_AGE = 2592000  # Persistencia por 30 días
SESSION_SAVE_EVERY_REQUEST = True

# ===== INTEGRACIÓN CON CRISPY FORMS =====
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'jalmeimag@gmail.com' 
EMAIL_HOST_PASSWORD = 'iefx kwgv baia djfm' 
DEFAULT_FROM_EMAIL = 'jalmeimag@gmail.com' 

SITE_URL = 'http://127.0.0.1:8000'


# Opción 2: Consola (Para pruebas - imprime emails en terminal)
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Opción 3: Archivo (Para pruebas - guarda emails en archivos)
# EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
# EMAIL_FILE_PATH = BASE_DIR / 'emails'