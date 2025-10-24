import sys
import os
from pathlib import Path
import environ
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Inicializamos environ
env = environ.Env(
    # Creamos valores por defecto y definimos el tipo de variable
    DEBUG=(bool, False)
)

# Leemos el archivo .env que está en la raíz del proyecto (BASE_DIR)
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG')

# Permitimos el acceso desde la URL de ngrok Y desde nuestro entorno de desarrollo local.
ALLOWED_HOSTS = [
    'ee22bfff0652.ngrok-free.app',  # Para los webhooks de WhatsApp
    'localhost',                   # Para acceder al admin desde tu navegador
    '127.0.0.1',                   # Alias de localhost, es bueno tenerlo también
]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'rest_framework',
    'rest_framework_simplejwt',  # NUEVO
    'rest_framework_simplejwt.token_blacklist',  # NUEVO
    'apps.core',
    'apps.custom_admin',
    'apps.authentication',
    'apps.orders',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'GraficaGyG_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'], 
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'GraficaGyG_backend.wsgi.application'

# Database
DATABASES = {
    'default': env.db( ),
}
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql_psycopg2',
#         'NAME': 'motelprats',  # El nombre de la base de datos que creamos
#         'USER': 'postgres',        # El usuario por defecto de PostgreSQL
#         'PASSWORD': '13940525', # ¡IMPORTANTE! Cambia esto por tu contraseña
#         'HOST': 'localhost',       # Donde está corriendo tu base de datos (normalmente localhost)
#         'PORT': '5432',            # El puerto por defecto de PostgreSQL
#     }
# }

# Password validation
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


# Internationalization
LANGUAGE_CODE = 'es-cl'
TIME_ZONE = 'America/Santiago'
USE_I18N = True
USE_TZ = True

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Configuración para Render
if 'RENDER' in os.environ:
    # Configuración de archivos estáticos para Render
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    STATIC_URL = '/static/'
    
    # Configuración de archivos media para Render
    MEDIA_ROOT = os.path.join(BASE_DIR, 'mediafiles')
    MEDIA_URL = '/media/'
    
    # Asegurar que los directorios existen
    os.makedirs(STATIC_ROOT, exist_ok=True)
    os.makedirs(MEDIA_ROOT, exist_ok=True)
else:
    # Configuración local (desarrollo)
    STATIC_URL = '/static/'
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    
    MEDIA_URL = '/media/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'mediafiles')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Configuración adicional para desarrollo
# ALLOWED_HOSTS = ['*']

# ==================== CONFIGURACIÓN CORS ====================
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# ==================== CONFIGURACIÓN REST FRAMEWORK ====================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',  # Por defecto permite todo
    ],
    'DEFAULT_PAGINATION_CLASS': None,  # ✅ DESACTIVA PAGINACIÓN
    # 'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    # 'PAGE_SIZE': 50,
}

# ==================== CONFIGURACIÓN JWT ====================
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=2),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

# ==================== CONFIGURACIÓN DE EMAIL ====================
# Para desarrollo: Console Backend (imprime en consola)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Para producción (Gmail ejemplo):
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='tu-email@gmail.com')
# EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='tu-app-password')
# DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='Gráfica GyG <tu-email@gmail.com>')

# URL del frontend para redirección después de validar email
FRONTEND_URL = env('FRONTEND_URL', default='http://localhost:5173')

# URL del backend para validación de email
BACKEND_URL = env('BACKEND_URL', default='http://localhost:8000')