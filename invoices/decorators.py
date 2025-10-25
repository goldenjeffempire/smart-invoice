"""
Custom decorators for the invoices app.
Provides performance monitoring, caching, and other cross-cutting concerns.
"""
import time
import logging
import functools
from typing import Callable, Any
from django.core.cache import cache
from django.conf import settings

logger = logging.getLogger(__name__)


def monitor_performance(func: Callable) -> Callable:
    """
    Decorator that monitors and logs function execution time.
    
    Args:
        func: The function to monitor.
        
    Returns:
        Wrapped function that logs execution time.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = (end_time - start_time) * 1000  # Convert to milliseconds
        
        logger.info(
            f"Performance: {func.__module__}.{func.__name__} "
            f"executed in {execution_time:.2f}ms"
        )
        
        # Log slow queries (>1000ms) as warnings
        if execution_time > 1000:
            logger.warning(
                f"Slow operation detected: {func.__module__}.{func.__name__} "
                f"took {execution_time:.2f}ms"
            )
        
        return result
    return wrapper


def cache_result(timeout: int = 300, key_prefix: str = ''):
    """
    Decorator that caches function results.
    
    Args:
        timeout: Cache timeout in seconds (default: 300 = 5 minutes).
        key_prefix: Optional prefix for cache key.
        
    Returns:
        Decorator function.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Generate cache key from function name and arguments
            cache_key = f"{key_prefix}{func.__module__}.{func.__name__}:"
            cache_key += str(args) + str(kwargs)
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, timeout)
            logger.debug(f"Cache miss for {func.__name__}, result cached")
            
            return result
        return wrapper
    return decorator


def log_exceptions(func: Callable) -> Callable:
    """
    Decorator that logs exceptions with full context.
    
    Args:
        func: The function to wrap.
        
    Returns:
        Wrapped function that logs exceptions.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(
                f"Exception in {func.__module__}.{func.__name__}: {str(e)}",
                exc_info=True,
                extra={
                    'function': func.__name__,
                    'module': func.__module__,
                    'args': str(args)[:200],  # Limit args length
                    'kwargs': str(kwargs)[:200],
                }
            )
            raise
    return wrapper


def require_feature(feature_flag: str):
    """
    Decorator that checks if a feature flag is enabled.
    
    Args:
        feature_flag: The name of the setting to check (e.g., 'PAYSTACK_SECRET_KEY').
        
    Returns:
        Decorator function.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            if not getattr(settings, feature_flag, None):
                raise ValueError(f"Feature not configured: {feature_flag}")
            return func(*args, **kwargs)
        return wrapper
    return decorator
