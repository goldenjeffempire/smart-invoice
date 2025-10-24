"""
Production settings for smart_invoice project.
"""

from .base import *
import dj_database_url
import logging

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Validate environment variables on startup (skip for management commands)
import sys
logger = logging.getLogger(__name__)

# Only validate when actually running the server (not during collectstatic, migrate, etc.)
is_management_command = 'manage.py' in sys.argv[0] if sys.argv else False
should_validate = not is_management_command or (is_management_command and any(cmd in sys.argv for cmd in ['runserver', 'gunicorn']))

if should_validate:
    try:
        from invoices.env_validator import EnvironmentValidator
        is_valid, errors, warnings = EnvironmentValidator.validate_all('production')
        
        if errors:
            logger.error("=" * 60)
            logger.error("ENVIRONMENT VALIDATION ERRORS:")
            for error in errors:
                logger.error(f"  {error}")
            logger.error("=" * 60)
            # Only raise error in actual deployment, not during checks
            if 'check' not in sys.argv:
                raise RuntimeError(
                    "Environment validation failed. Fix the errors above before deploying to production."
                )
        
        if warnings:
            logger.warning("=" * 60)
            logger.warning("ENVIRONMENT VALIDATION WARNINGS:")
            for warning in warnings:
                logger.warning(f"  {warning}")
            logger.warning("=" * 60)
    except ImportError:
        logger.warning("Environment validator not available - skipping validation")

# Allowed hosts - should be set via environment variable
ALLOWED_HOSTS = os.environ.get(
    'DJANGO_ALLOWED_HOSTS',
    '.onrender.com,.herokuapp.com'
).split(',')

# Database - PostgreSQL for production
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=600,
        conn_health_checks=True,
        ssl_require=True,
    )
}

# Email backend - SMTP for production
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER)

# Static files - compressed and cached for production
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# CSRF Trusted Origins
CSRF_TRUSTED_ORIGINS = os.environ.get(
    'CSRF_TRUSTED_ORIGINS',
    'https://*.onrender.com,https://*.herokuapp.com'
).split(',')

# Frame Options - Deny for production security
X_FRAME_OPTIONS = 'DENY'

# Production Security Settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# Security Middleware Settings
SECURE_REFERRER_POLICY = 'same-origin'

# Session security
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = 'Lax'

# Logging Configuration - production logging (console only for Render's ephemeral filesystem)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
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
        'django.security': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'invoices': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Cache Configuration for Production
# Database cache is always the default (required for Django admin, sessions, etc.)
# Redis is configured as a separate 'redis' cache for rate limiting if available
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

# Add Redis cache as separate alias if available (used for rate limiting)
if REDIS_URL:
    try:
        CACHES['redis'] = {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': REDIS_URL,
            'KEY_PREFIX': 'smart_invoice',
            'TIMEOUT': 300,
        }
        # Use Redis for rate limiting (better for multi-worker scenarios)
        RATE_LIMIT_CACHE = 'redis'
    except ImportError:
        # Redis library not installed, fall back to default cache
        RATE_LIMIT_CACHE = 'default'
else:
    RATE_LIMIT_CACHE = 'default'
