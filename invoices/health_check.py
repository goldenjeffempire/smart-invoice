"""
Health check utilities for Smart Invoice platform.
Used by load balancers, monitoring systems, and deployment platforms.
"""
from django.db import connection
from django.core.cache import cache
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def check_database():
    """Check database connectivity."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return True, "Database OK"
    except Exception as e:
        logger.error(f'Database health check failed: {str(e)}')
        return False, f"Database error: {str(e)}"


def check_cache():
    """Check cache system."""
    try:
        cache.set('health_check', 'ok', 10)
        value = cache.get('health_check')
        if value == 'ok':
            return True, "Cache OK"
        return False, "Cache read/write failed"
    except Exception as e:
        logger.error(f'Cache health check failed: {str(e)}')
        return False, f"Cache error: {str(e)}"


def check_paystack_config():
    """Check Paystack configuration."""
    if settings.PAYSTACK_SECRET_KEY and settings.PAYSTACK_PUBLIC_KEY:
        return True, "Paystack configured"
    return False, "Paystack not configured"


def check_email_config():
    """Check email configuration."""
    if settings.EMAIL_HOST and settings.EMAIL_HOST_USER:
        return True, "Email configured"
    return False, "Email not configured"


def run_all_health_checks():
    """Run all health checks and return status."""
    checks = {
        'database': check_database(),
        'cache': check_cache(),
        'paystack': check_paystack_config(),
        'email': check_email_config(),
    }
    
    all_passing = all(status for status, _ in checks.values())
    
    return {
        'status': 'healthy' if all_passing else 'degraded',
        'checks': {
            name: {'passing': status, 'message': message}
            for name, (status, message) in checks.items()
        }
    }
