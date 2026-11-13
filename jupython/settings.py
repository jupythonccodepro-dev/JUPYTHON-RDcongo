"""
Django settings for jupython project.

Généré avec « django-admin startproject » et Django 6.0.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

import os
from datetime import timedelta
from pathlib import Path
from urllib.parse import urlsplit

from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

# Construire les chemins du projet à partir de BASE_DIR, par exemple BASE_DIR / 'sous_dossier'.
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')


# Paramètres de démarrage rapide pour le développement — à adapter avant la production.
# Voir https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/

# AVERTISSEMENT DE SÉCURITÉ : garder secrète la clé utilisée en production.
SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DEBUG', 'False').lower() in {'1', 'true', 'yes', 'on'}
if not SECRET_KEY:
    if not DEBUG:
        raise ImproperlyConfigured('SECRET_KEY doit être configurée lorsque DEBUG est désactivé.')
    SECRET_KEY = 'django-insecure-local-development-only'

GOOGLE_CLIENT_ID = (os.getenv('GOOGLE_CLIENT_ID') or '').strip()

# AVERTISSEMENT DE SÉCURITÉ : ne pas activer le mode debug en production.


def _env_bool(name, default):
    value = os.getenv(name)
    if value is None:
        return default
    normalized = value.strip().lower()
    if normalized in {'1', 'true', 'yes', 'on'}:
        return True
    if normalized in {'0', 'false', 'no', 'off'}:
        return False
    raise ImproperlyConfigured(f'{name} doit être définie sur true ou false.')


def _env_list(name, default=''):
    value = os.getenv(name, default)
    return [item.strip() for item in value.split(',') if item.strip()]


def _validate_https_origins(name, origins):
    for origin in origins:
        parsed_origin = urlsplit(origin)
        if (
            parsed_origin.scheme != 'https'
            or not parsed_origin.hostname
            or parsed_origin.path not in {'', '/'}
            or parsed_origin.query
            or parsed_origin.fragment
        ):
            raise ImproperlyConfigured(f'{name} doit contenir uniquement des origines HTTPS valides.')


ALLOWED_HOSTS = _env_list(
    'ALLOWED_HOSTS',
    '127.0.0.1,localhost,testserver' if DEBUG else '',
)
CSRF_TRUSTED_ORIGINS = _env_list(
    'CSRF_TRUSTED_ORIGINS',
    'http://localhost:8000,http://127.0.0.1:8000' if DEBUG else '',
)


# Définition des applications

# Courriels d’authentification (mot de passe oublié et réinitialisation).
EMAIL_BACKEND = os.getenv(
    'EMAIL_BACKEND',
    'django.core.mail.backends.console.EmailBackend' if DEBUG else 'django.core.mail.backends.smtp.EmailBackend',
)
EMAIL_HOST = os.getenv('EMAIL_HOST', '')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = _env_bool('EMAIL_USE_TLS', not DEBUG)
EMAIL_USE_SSL = _env_bool('EMAIL_USE_SSL', False)
EMAIL_TIMEOUT = int(os.getenv('EMAIL_TIMEOUT', '10'))
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER or 'Jupython Academy <no-reply@localhost>')
MAINTENANCE_REPORT_EMAIL = os.getenv('MAINTENANCE_REPORT_EMAIL', '')
if EMAIL_USE_TLS and EMAIL_USE_SSL:
    raise ImproperlyConfigured('EMAIL_USE_TLS et EMAIL_USE_SSL ne peuvent pas être activés ensemble.')

INSTALLED_APPS = [
    'corsheaders',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt.token_blacklist',
    'core',
    'accounts',
    'academy',
    'ranking',
    'frontend',
]

AUTH_USER_MODEL = 'accounts.User'


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

# Google Identity Services doit pouvoir communiquer avec sa fenêtre de connexion.
SECURE_CROSS_ORIGIN_OPENER_POLICY = 'same-origin-allow-popups'

SECURE_SSL_REDIRECT = _env_bool('SECURE_SSL_REDIRECT', not DEBUG)
SESSION_COOKIE_SECURE = _env_bool('SESSION_COOKIE_SECURE', not DEBUG)
CSRF_COOKIE_SECURE = _env_bool('CSRF_COOKIE_SECURE', not DEBUG)
try:
    SECURE_HSTS_SECONDS = int(os.getenv('SECURE_HSTS_SECONDS', '0'))
except ValueError as exc:
    raise ImproperlyConfigured('SECURE_HSTS_SECONDS doit être un entier positif ou nul.') from exc
if SECURE_HSTS_SECONDS < 0:
    raise ImproperlyConfigured('SECURE_HSTS_SECONDS doit être un entier positif ou nul.')
SECURE_HSTS_INCLUDE_SUBDOMAINS = _env_bool('SECURE_HSTS_INCLUDE_SUBDOMAINS', False)
SECURE_HSTS_PRELOAD = _env_bool('SECURE_HSTS_PRELOAD', False)
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

if not DEBUG:
    if (
        not SECRET_KEY
        or len(SECRET_KEY) < 50
        or SECRET_KEY.startswith('django-insecure-')
        or 'remplacer-par-' in SECRET_KEY.lower()
    ):
        raise ImproperlyConfigured(
            'Configurez une SECRET_KEY de production aléatoire d’au moins 50 caractères et gardée secrète.'
        )
    if not ALLOWED_HOSTS:
        raise ImproperlyConfigured('Configurez ALLOWED_HOSTS avec les noms d’hôte exacts du site en production.')
    if '*' in ALLOWED_HOSTS:
        raise ImproperlyConfigured('ALLOWED_HOSTS ne peut pas contenir * en production.')
    if not SECURE_SSL_REDIRECT or not SESSION_COOKIE_SECURE or not CSRF_COOKIE_SECURE:
        raise ImproperlyConfigured(
            'En production, SECURE_SSL_REDIRECT, SESSION_COOKIE_SECURE et CSRF_COOKIE_SECURE doivent être activés.'
        )
    _validate_https_origins('CSRF_TRUSTED_ORIGINS', CSRF_TRUSTED_ORIGINS)

# À définir uniquement si Django est derrière un mandataire inverse de confiance qui termine TLS.
secure_proxy_ssl_header = os.getenv('SECURE_PROXY_SSL_HEADER', '').strip()
if secure_proxy_ssl_header:
    proxy_header_parts = [part.strip() for part in secure_proxy_ssl_header.split(',', maxsplit=1)]
    if len(proxy_header_parts) != 2 or not all(proxy_header_parts):
        raise ImproperlyConfigured(
            'SECURE_PROXY_SSL_HEADER doit contenir un nom d’en-tête et sa valeur, séparés par une virgule, '
            'par exemple HTTP_X_FORWARDED_PROTO,https.'
        )
    SECURE_PROXY_SSL_HEADER = (proxy_header_parts[0], proxy_header_parts[1])

CORS_ALLOWED_ORIGINS = _env_list(
    'CORS_ALLOWED_ORIGINS',
    'http://localhost:3000,http://127.0.0.1:3000' if DEBUG else '',
)
if not DEBUG:
    _validate_https_origins('CORS_ALLOWED_ORIGINS', CORS_ALLOWED_ORIGINS)

# Django REST Framework et JWT
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_THROTTLE_RATES': {
        'login': '5/minute',
        'password_reset': '5/hour',
        'password_change': '5/hour',
    },
}
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}

ROOT_URLCONF = 'jupython.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [BASE_DIR / 'templates', BASE_DIR / 'frontend' / 'frontend'],
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

WSGI_APPLICATION = 'jupython.wsgi.application'


# PostgreSQL est le seul moteur de base de données pris en charge.
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
if not DEBUG and (not DB_PASSWORD or 'remplacer-par-' in DB_PASSWORD.lower()):
    raise ImproperlyConfigured('Configurez un mot de passe PostgreSQL de production.')
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'jupython'),
        'USER': os.getenv('DB_USER', 'jupython'),
        'PASSWORD': DB_PASSWORD,
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
        'CONN_MAX_AGE': 60,
        'OPTIONS': {'connect_timeout': 5},
    }
}

# Validation des mots de passe
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

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



# Internationalisation
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'fr-fr'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Fichiers statiques (CSS, JavaScript, images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = '/assets/'

# Emplacement des fichiers statiques issus du frontend (dev)
STATICFILES_DIRS = [
    BASE_DIR / 'frontend' / 'frontend' / 'assets',
]

# Racine de collecte des fichiers statiques (pour collectstatic en production)
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
PRIVATE_CERTIFICATES_ROOT = BASE_DIR / '.private-certificates'

# Type de champ de clé primaire par défaut
# https://docs.djangoproject.com/en/6.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
