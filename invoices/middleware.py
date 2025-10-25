"""
Custom middleware for security, rate limiting, and audit logging.
Provides comprehensive protection and monitoring for the Django application.
"""
from django.core.cache import cache, caches
from django.http import HttpResponseForbidden
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
import logging
import hashlib

logger = logging.getLogger(__name__)


class RateLimitMiddleware(MiddlewareMixin):
    """
    Rate limiting middleware to prevent abuse and brute force attacks.
    
    Tracks requests by IP address and enforces configurable rate limits on
    sensitive endpoints. Uses Redis cache when available for better performance
    across multiple application instances.
    
    Settings:
        RATE_LIMIT_MAX_REQUESTS: Max requests per window (default: 60)
        RATE_LIMIT_WINDOW: Time window in seconds (default: 60)
        RATE_LIMIT_CACHE: Cache backend to use (default: 'default')
    """
    def process_request(self, request):
        if settings.DEBUG:
            return None
        
        rate_limit_endpoints = [
            '/login/',
            '/signup/',
            '/invoice/pay/',
            '/payment/callback/',
        ]
        
        is_rate_limited = any(request.path.startswith(endpoint) for endpoint in rate_limit_endpoints)
        
        if not is_rate_limited:
            return None
        
        ip_address = self.get_client_ip(request)
        cache_key = f'rate_limit_{hashlib.md5(ip_address.encode()).hexdigest()}_{request.path}'
        
        cache_backend = getattr(settings, 'RATE_LIMIT_CACHE', 'default')
        rate_cache = caches[cache_backend]
        
        requests_count = rate_cache.get(cache_key, 0)
        
        limit = getattr(settings, 'RATE_LIMIT_MAX_REQUESTS', 60)
        window = getattr(settings, 'RATE_LIMIT_WINDOW', 60)
        
        if requests_count >= limit:
            logger.warning(f'Rate limit exceeded for IP: {ip_address} on {request.path}')
            return HttpResponseForbidden('Rate limit exceeded. Please try again later.')
        
        rate_cache.set(cache_key, requests_count + 1, window)
        
        return None
    
    def get_client_ip(self, request):
        """Get client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Security headers middleware for enhanced protection.
    
    Adds security headers to all responses in production mode to protect against
    common web vulnerabilities like XSS, clickjacking, and MIME-type sniffing.
    
    Headers Added:
        - X-Content-Type-Options: nosniff
        - X-Frame-Options: DENY
        - X-XSS-Protection: 1; mode=block
        - Referrer-Policy: strict-origin-when-cross-origin
        - Permissions-Policy: geolocation=(), microphone=(), camera=()
    """
    def process_response(self, request, response):
        if not settings.DEBUG:
            response['X-Content-Type-Options'] = 'nosniff'
            response['X-Frame-Options'] = 'DENY'
            response['X-XSS-Protection'] = '1; mode=block'
            response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
            response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
            
        return response


class AuditLogMiddleware(MiddlewareMixin):
    """
    Audit logging middleware for tracking sensitive operations.
    
    Logs all POST, PUT, DELETE, and PATCH requests to sensitive endpoints,
    capturing user information and IP addresses for security monitoring
    and compliance purposes.
    
    Monitored Paths:
        - /invoice/delete/
        - /client/delete/
        - /invoice/
        - /admin/
    """
    def process_request(self, request):
        if request.user.is_authenticated:
            sensitive_paths = [
                '/invoice/delete/',
                '/client/delete/',
                '/invoice/',
                '/admin/',
            ]
            
            is_sensitive = any(request.path.startswith(path) for path in sensitive_paths)
            
            if is_sensitive and request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
                x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
                ip_address = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')
                logger.info(
                    f'Audit: User {request.user.username} performed {request.method} on {request.path} '
                    f'from IP {ip_address}'
                )
        
        return None
