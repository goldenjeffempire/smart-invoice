from django.http import JsonResponse
from django.db import connection
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def health_check(request):
    health_status = {
        'status': 'healthy',
        'database': 'unknown',
        'environment': settings.DJANGO_ENV if hasattr(settings, 'DJANGO_ENV') else 'unknown',
    }
    
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
            health_status['database'] = 'connected'
    except Exception as e:
        logger.error(f'Database health check failed: {str(e)}')
        health_status['database'] = 'disconnected'
        health_status['status'] = 'unhealthy'
        return JsonResponse(health_status, status=503)
    
    return JsonResponse(health_status)


def readiness_check(request):
    readiness_status = {
        'ready': True,
        'checks': {
            'database': False,
            'migrations': False,
        }
    }
    
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
            readiness_status['checks']['database'] = True
    except Exception as e:
        logger.error(f'Database readiness check failed: {str(e)}')
        readiness_status['ready'] = False
    
    try:
        from django.db.migrations.executor import MigrationExecutor
        executor = MigrationExecutor(connection)
        plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
        readiness_status['checks']['migrations'] = len(plan) == 0
        if len(plan) > 0:
            readiness_status['ready'] = False
    except Exception as e:
        logger.error(f'Migration check failed: {str(e)}')
        readiness_status['ready'] = False
    
    status_code = 200 if readiness_status['ready'] else 503
    return JsonResponse(readiness_status, status=status_code)
