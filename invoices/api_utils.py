"""
API utilities for standardized error responses and HTTP status codes.
Provides consistent JSON API responses across the application.
"""
from typing import Dict, Any, Optional
from django.http import JsonResponse
from django.core.serializers.json import DjangoJSONEncoder
import logging

logger = logging.getLogger(__name__)


class APIResponse:
    """
    Standardized API response builder for consistent JSON responses.
    
    Provides static methods for common HTTP responses with proper status codes
    and consistent JSON structure.
    """
    
    @staticmethod
    def success(data: Any = None, message: str = "Success", status: int = 200) -> JsonResponse:
        """
        Create a successful API response.
        
        Args:
            data: The response data (can be dict, list, or any JSON-serializable type).
            message: Success message (default: "Success").
            status: HTTP status code (default: 200).
            
        Returns:
            JsonResponse with success structure.
        """
        response_data = {
            'success': True,
            'message': message,
            'data': data
        }
        return JsonResponse(response_data, status=status, encoder=DjangoJSONEncoder)
    
    @staticmethod
    def error(
        message: str,
        errors: Optional[Dict[str, Any]] = None,
        status: int = 400
    ) -> JsonResponse:
        """
        Create an error API response.
        
        Args:
            message: Error message describing what went wrong.
            errors: Optional dict of detailed field-level errors.
            status: HTTP status code (default: 400 Bad Request).
            
        Returns:
            JsonResponse with error structure.
        """
        response_data = {
            'success': False,
            'message': message,
            'errors': errors or {}
        }
        logger.warning(f"API error response: {message} (status: {status})")
        return JsonResponse(response_data, status=status)
    
    @staticmethod
    def not_found(message: str = "Resource not found") -> JsonResponse:
        """
        Create a 404 Not Found response.
        
        Args:
            message: Error message (default: "Resource not found").
            
        Returns:
            JsonResponse with 404 status.
        """
        return APIResponse.error(message, status=404)
    
    @staticmethod
    def unauthorized(message: str = "Authentication required") -> JsonResponse:
        """
        Create a 401 Unauthorized response.
        
        Args:
            message: Error message (default: "Authentication required").
            
        Returns:
            JsonResponse with 401 status.
        """
        return APIResponse.error(message, status=401)
    
    @staticmethod
    def forbidden(message: str = "Permission denied") -> JsonResponse:
        """
        Create a 403 Forbidden response.
        
        Args:
            message: Error message (default: "Permission denied").
            
        Returns:
            JsonResponse with 403 status.
        """
        return APIResponse.error(message, status=403)
    
    @staticmethod
    def bad_request(message: str, errors: Optional[Dict[str, Any]] = None) -> JsonResponse:
        """
        Create a 400 Bad Request response.
        
        Args:
            message: Error message describing the invalid request.
            errors: Optional dict of validation errors.
            
        Returns:
            JsonResponse with 400 status.
        """
        return APIResponse.error(message, errors=errors, status=400)
    
    @staticmethod
    def server_error(message: str = "Internal server error") -> JsonResponse:
        """
        Create a 500 Internal Server Error response.
        
        Args:
            message: Error message (default: "Internal server error").
            
        Returns:
            JsonResponse with 500 status.
        """
        logger.error(f"Server error: {message}")
        return APIResponse.error(message, status=500)
    
    @staticmethod
    def created(data: Any = None, message: str = "Resource created successfully") -> JsonResponse:
        """
        Create a 201 Created response.
        
        Args:
            data: The created resource data.
            message: Success message (default: "Resource created successfully").
            
        Returns:
            JsonResponse with 201 status.
        """
        return APIResponse.success(data, message, status=201)
    
    @staticmethod
    def no_content() -> JsonResponse:
        """
        Create a 204 No Content response.
        
        Returns:
            JsonResponse with 204 status and empty body.
        """
        return JsonResponse({}, status=204)
