"""
Django settings for eventos_app project.
"""

from pathlib import Path
import os  # Necesario para construir rutas

# Base directory del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

# Clave secreta (no la muestres en producción)
SECRET_KEY = 'django-insecure-uow^wmt=ze0&90ixxpvlflxe)_ol7!8)j=&a2ck&cd*qf3)gv*'

# Modo de desarrollo
DEBUG = True

ALLOWED_HOSTS = []

# Aplicaciones instaladas
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'eventos',  # 👈 Tu app personalizada debe ir aquí
    'rest_framework',
]

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'eventos_app.urls'

# Configuración de plantillas
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],  # ✅ Ruta a tus plantillas personalizadas
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',  # útil para depurar
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'eventos_app.wsgi.application'

# Base de datos (SQLite por defecto)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Validaciones de contraseña
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Configuración regional
LANGUAGE_CODE = 'es-es'  # puedes dejarlo en 'en-us' si prefieres
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Archivos estáticos (CSS, JS, imágenes)
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]  # ✅ Opcional: si usarás carpeta static/

# Clave por defecto para campos auto
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_REDIRECT_URL = '/eventos/'
LOGOUT_REDIRECT_URL = '/accounts/login/'  # A dónde ir después de cerrar sesión
LOGIN_URL = '/accounts/login/'  # A dónde ir si alguien no autenticado intenta acceder a una vista protegida

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Configuración de correo electrónico SMTP (ejemplo para Gmail)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'jfortiz@tes.edu.ec'  # Cambia por tu correo real
EMAIL_HOST_PASSWORD = 'hkvbymtxwureyhzg'  # Cambia por tu contraseña o token
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# Configuración de JWT para autenticación
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    )
}
