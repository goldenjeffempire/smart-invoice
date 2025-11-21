from django.http import JsonResponse
from django.db import connection
from django.conf import settings
import sys


def health_check(request):
    """
    Health check endpoint for monitoring and load balancers.
    Returns service status, database connectivity, and basic system info.
    """
    health_status = {
        "status": "healthy",
        "service": "smart-invoice",
        "version": "1.0.0",
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "debug": settings.DEBUG,
    }

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            health_status["database"] = "connected"
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["database"] = "disconnected"
        health_status["error"] = str(e)
        return JsonResponse(health_status, status=503)

    return JsonResponse(health_status, status=200)


def readiness_check(request):
    """
    Readiness check for Kubernetes/container orchestration.
    Verifies the app is ready to receive traffic.
    """
    checks = {
        "database": False,
        "migrations": False,
    }

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            checks["database"] = True
    except Exception:
        pass

    try:
        from django.db.migrations.executor import MigrationExecutor
        executor = MigrationExecutor(connection)
        plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
        checks["migrations"] = len(plan) == 0
    except Exception:
        pass

    all_ready = all(checks.values())
    status_code = 200 if all_ready else 503

    return JsonResponse(
        {
            "ready": all_ready,
            "checks": checks,
        },
        status=status_code,
    )


def liveness_check(request):
    """
    Liveness check for Kubernetes/container orchestration.
    Verifies the app is alive and not deadlocked.
    """
    return JsonResponse({"alive": True}, status=200)
