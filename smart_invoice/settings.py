"""
Django settings for smart_invoice project.
Auto-detects environment and configures accordingly.
"""

from pathlib import Path
import os
import logging
import dj_database_url
from django.core.management.utils import get_random_secret_key
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Detect environment
ENV = os.environ.get('DJANGO_ENV', 'development')
IS_PRODUCTION = ENV == 'production'
IS_DEVELOPMENT = not IS_PRODUCTION

# ==============================================================================
# CORE SETTINGS
# ==============================================================================

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY') or os.environ.get('SECRET_KEY') or get_random_secret_key()

# Debug mode
DEBUG = False if IS_PRODUCTION else True

# Allowed hosts
if IS_PRODUCTION:
    ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '.onrender.com,.herokuapp.com').split(',')
else:
    ALLOWED_HOSTS = ['*']  # Allow all in development (Replit uses dynamic subdomains)

# ==============================================================================
# APPLICATION DEFINITION
# ==============================================================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'invoices',
    'crispy_forms',
    'widget_tweaks',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'invoices.middleware.SecurityHeadersMiddleware',
    'invoices.middleware.RateLimitMiddleware',
    'invoices.middleware.AuditLogMiddleware',
]

ROOT_URLCONF = 'smart_invoice.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'invoices' / 'templates'],
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

WSGI_APPLICATION = 'smart_invoice.wsgi.application'

# ==============================================================================
# DATABASE CONFIGURATION
# ==============================================================================

if IS_PRODUCTION:
    # Production: Use PostgreSQL via DATABASE_URL, fallback to SQLite for initial deployment
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        DATABASES = {
            'default': dj_database_url.config(
                default=database_url,
                conn_max_age=600,
                conn_health_checks=True,
                ssl_require=True,
            )
        }
    else:
        # Temporary fallback to SQLite for initial deployment
        logger = logging.getLogger(__name__)
        logger.warning("⚠️  DATABASE_URL not set - using temporary SQLite database")
        logger.warning("    Please configure PostgreSQL via Render dashboard for production use")
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'db.sqlite3',
            }
        }
else:
    # Development: Use SQLite
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# ==============================================================================
# PASSWORD VALIDATION
# ==============================================================================

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

# ==============================================================================
# INTERNATIONALIZATION
# ==============================================================================

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ==============================================================================
# STATIC FILES (CSS, JavaScript, Images)
# ==============================================================================

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Additional static files locations
STATICFILES_DIRS = []

# Static files storage
if IS_PRODUCTION:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
else:
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# ==============================================================================
# MEDIA FILES
# ==============================================================================

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ==============================================================================
# DEFAULT PRIMARY KEY FIELD TYPE
# ==============================================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ==============================================================================
# SECURITY SETTINGS
# ==============================================================================

if IS_PRODUCTION:
    # Production security settings
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_REFERRER_POLICY = 'same-origin'
    SESSION_COOKIE_SAMESITE = 'Lax'
    CSRF_COOKIE_SAMESITE = 'Lax'
    X_FRAME_OPTIONS = 'DENY'
    
    # CSRF Trusted Origins
    CSRF_TRUSTED_ORIGINS = os.environ.get(
        'CSRF_TRUSTED_ORIGINS',
        'https://*.onrender.com,https://*.herokuapp.com'
    ).split(',')
else:
    # Development security settings (relaxed)
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    SECURE_SSL_REDIRECT = False
    X_FRAME_OPTIONS = 'SAMEORIGIN'
    
    # CSRF Trusted Origins for Replit
    CSRF_TRUSTED_ORIGINS = [
        'https://*.replit.dev',
        'https://*.repl.co',
    ]

# CSRF Cookie HTTP Only
CSRF_COOKIE_HTTPONLY = True

# ==============================================================================
# EMAIL CONFIGURATION
# ==============================================================================

if IS_PRODUCTION:
    # Production: SMTP
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
    EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
    EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
    EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
    DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER)
else:
    # Development: Console backend (emails print to console)
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
    EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
    EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
    EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
    EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')

# ==============================================================================
# CACHE CONFIGURATION
# ==============================================================================

if IS_PRODUCTION:
    # Production: Database cache with optional Redis
    REDIS_URL = os.environ.get('REDIS_URL')
    
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
            'LOCATION': 'cache_table',
            'OPTIONS': {
                'MAX_ENTRIES': 5000,
                'CULL_FREQUENCY': 3,
            }
        }
    }
    
    # Add Redis cache as separate alias if available
    if REDIS_URL:
        try:
            CACHES['redis'] = {
                'BACKEND': 'django.core.cache.backends.redis.RedisCache',
                'LOCATION': REDIS_URL,
                'KEY_PREFIX': 'smart_invoice',
                'TIMEOUT': 300,
            }
            RATE_LIMIT_CACHE = 'redis'
        except ImportError:
            RATE_LIMIT_CACHE = 'default'
    else:
        RATE_LIMIT_CACHE = 'default'
else:
    # Development: Dummy cache (no caching)
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    }
    RATE_LIMIT_CACHE = 'default'

# ==============================================================================
# LOGGING CONFIGURATION
# ==============================================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}' if IS_DEVELOPMENT else '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'WARNING' if IS_PRODUCTION else 'WARNING',  # Set to DEBUG to see SQL queries
            'propagate': False,
        },
        'django.security': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'invoices': {
            'handlers': ['console'],
            'level': 'INFO' if IS_PRODUCTION else 'DEBUG',
            'propagate': False,
        },
    },
}

# ==============================================================================
# THIRD-PARTY APP SETTINGS
# ==============================================================================

# Crispy Forms
CRISPY_TEMPLATE_PACK = 'bootstrap4'

# ==============================================================================
# APPLICATION-SPECIFIC SETTINGS
# ==============================================================================

# Paystack Configuration
PAYSTACK_PUBLIC_KEY = os.environ.get('PAYSTACK_PUBLIC_KEY', '')
PAYSTACK_SECRET_KEY = os.environ.get('PAYSTACK_SECRET_KEY', '')
PAYSTACK_WEBHOOK_SECRET = os.environ.get('PAYSTACK_WEBHOOK_SECRET', '')

# Twilio Configuration
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID', '')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN', '')
TWILIO_WHATSAPP_NUMBER = os.environ.get('TWILIO_WHATSAPP_NUMBER', '')

# WhatsApp Configuration
WHATSAPP_NUMBER = os.environ.get('WHATSAPP_NUMBER', '')

# Site Configuration
SITE_URL = os.environ.get('SITE_URL', 'http://localhost:5000')

# Cloudinary Configuration (for PDF storage)
CLOUDINARY_URL = os.environ.get('CLOUDINARY_URL', '')
CLOUDINARY_CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME', '')
CLOUDINARY_API_KEY = os.environ.get('CLOUDINARY_API_KEY', '')
CLOUDINARY_API_SECRET = os.environ.get('CLOUDINARY_API_SECRET', '')

# ==============================================================================
# ENVIRONMENT VALIDATION (Production Only)
# ==============================================================================

if IS_PRODUCTION:
    logger = logging.getLogger(__name__)
    
    # Check for critical environment variables and warn if missing
    try:
        from invoices.env_validator import EnvironmentValidator
        is_valid, errors, warnings = EnvironmentValidator.validate_all('production')
        
        if errors:
            logger.error("=" * 60)
            logger.error("ENVIRONMENT VALIDATION ERRORS:")
            for error in errors:
                logger.error(f"  {error}")
            logger.error("=" * 60)
            logger.error("⚠️  Please set the required environment variables in your deployment dashboard!")
            logger.error("    The application may not function correctly until these are configured.")
        
        if warnings:
            logger.warning("=" * 60)
            logger.warning("ENVIRONMENT VALIDATION WARNINGS:")
            for warning in warnings:
                logger.warning(f"  {warning}")
            logger.warning("=" * 60)
    except ImportError:
        logger.warning("Environment validator not available - skipping validation")
