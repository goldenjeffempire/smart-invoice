"""
Custom security middleware for Smart Invoice.
Implements additional security headers and logging.
"""
import logging
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Add security headers to all responses.
    
    Headers implemented:
    - X-Content-Type-Options: nosniff
    - X-Frame-Options: DENY (prevent clickjacking)
    - Referrer-Policy: strict-origin-when-cross-origin
    - Permissions-Policy: Restrict browser features
    """

    def process_response(self, request, response):
        response["X-Content-Type-Options"] = "nosniff"
        response["X-Frame-Options"] = "DENY"
        response["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response["Permissions-Policy"] = (
            "geolocation=(), microphone=(), camera=(), payment=()"
        )
        
        if not request.is_secure() and not request.get_host().startswith("localhost"):
            response["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains; preload"
            )
        
        return response


class SecurityEventLoggingMiddleware(MiddlewareMixin):
    """
    Log security-relevant events for monitoring and audit trails.
    """

    def process_request(self, request):
        # Skip logging for test environment
        if 'test' in request.META.get('SERVER_NAME', ''):
            return None
            
        if request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            logger.info(
                f"Security Event: {request.method} {request.path} "
                f"from {self.get_client_ip(request)} "
                f"user={request.user.username if request.user.is_authenticated else 'anonymous'}"
            )
        return None

    def process_response(self, request, response):
        # Skip logging for test environment
        if 'test' in request.META.get('SERVER_NAME', ''):
            return response
            
        if response.status_code >= 400:
            logger.warning(
                f"HTTP {response.status_code}: {request.method} {request.path} "
                f"from {self.get_client_ip(request)} "
                f"user={request.user.username if request.user.is_authenticated else 'anonymous'}"
            )
        return response

    @staticmethod
    def get_client_ip(request):
        """Extract client IP from request headers."""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0].strip()
        else:
            ip = request.META.get("REMOTE_ADDR", "unknown")
        return ip
