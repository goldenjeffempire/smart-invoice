"""
Environment variable validation for Smart Invoice platform.
Validates all required configuration on application startup.
"""
import os
import logging
from typing import List, Dict, Tuple

logger = logging.getLogger(__name__)


class EnvironmentValidator:
    """Validates environment variables on application startup."""
    
    # Required environment variables for all environments
    REQUIRED_VARS = [
        'DJANGO_SECRET_KEY',
    ]
    
    # Required for production environment
    PRODUCTION_REQUIRED_VARS = [
        'DATABASE_URL',
        'DJANGO_ALLOWED_HOSTS',
        'SITE_URL',
    ]
    
    # Optional but recommended for production
    PRODUCTION_RECOMMENDED_VARS = [
        'EMAIL_HOST_USER',
        'EMAIL_HOST_PASSWORD',
        'PAYSTACK_PUBLIC_KEY',
        'PAYSTACK_SECRET_KEY',
        'WHATSAPP_NUMBER',
    ]
    
    # Warning if these are missing (won't break app but limits functionality)
    OPTIONAL_FEATURE_VARS = {
        'PAYSTACK_PUBLIC_KEY': 'Payment processing via Paystack will be disabled',
        'PAYSTACK_SECRET_KEY': 'Payment processing via Paystack will be disabled',
        'EMAIL_HOST_USER': 'Email invoice delivery will be disabled',
        'EMAIL_HOST_PASSWORD': 'Email invoice delivery will be disabled',
        'WHATSAPP_NUMBER': 'WhatsApp Pay Now button will be hidden',
        'TWILIO_ACCOUNT_SID': 'WhatsApp invoice delivery via Twilio will be disabled',
        'TWILIO_AUTH_TOKEN': 'WhatsApp invoice delivery via Twilio will be disabled',
    }
    
    @classmethod
    def validate_all(cls, environment: str = 'development') -> Tuple[bool, List[str], List[str]]:
        """
        Validate all environment variables.
        
        Args:
            environment: 'development' or 'production'
            
        Returns:
            Tuple of (is_valid, errors, warnings)
        """
        errors = []
        warnings = []
        
        # Check required variables
        for var in cls.REQUIRED_VARS:
            if not os.environ.get(var):
                errors.append(f"❌ REQUIRED: {var} is not set")
        
        # Check production-specific requirements
        if environment == 'production':
            for var in cls.PRODUCTION_REQUIRED_VARS:
                if not os.environ.get(var):
                    errors.append(f"❌ PRODUCTION REQUIRED: {var} is not set")
            
            for var in cls.PRODUCTION_RECOMMENDED_VARS:
                if not os.environ.get(var):
                    warnings.append(f"⚠️  RECOMMENDED: {var} is not set")
        
        # Check optional feature variables
        for var, message in cls.OPTIONAL_FEATURE_VARS.items():
            if not os.environ.get(var):
                warnings.append(f"ℹ️  OPTIONAL: {var} is not set - {message}")
        
        # Validate specific configurations
        cls._validate_secret_key(errors, warnings)
        cls._validate_debug_setting(errors, warnings, environment)
        cls._validate_database_url(errors, warnings, environment)
        cls._validate_email_config(warnings)
        cls._validate_paystack_config(warnings)
        
        is_valid = len(errors) == 0
        return is_valid, errors, warnings
    
    @classmethod
    def _validate_secret_key(cls, errors: List[str], warnings: List[str]):
        """Validate Django secret key."""
        secret_key = os.environ.get('DJANGO_SECRET_KEY', '')
        
        if secret_key:
            if len(secret_key) < 32:
                warnings.append(
                    "⚠️  DJANGO_SECRET_KEY is too short (should be at least 32 characters)"
                )
            
            if secret_key in ['your-secret-key', 'changeme', 'insecure']:
                errors.append(
                    "❌ DJANGO_SECRET_KEY contains an insecure default value - please change it!"
                )
    
    @classmethod
    def _validate_debug_setting(cls, errors: List[str], warnings: List[str], environment: str):
        """Validate DEBUG setting."""
        # Check both DEBUG and DJANGO_DEBUG for compatibility
        debug = os.environ.get('DJANGO_DEBUG', os.environ.get('DEBUG', '')).lower()
        
        if environment == 'production' and debug == 'true':
            errors.append(
                "❌ DEBUG/DJANGO_DEBUG=True in production environment! This is a security risk."
            )
    
    @classmethod
    def _validate_database_url(cls, errors: List[str], warnings: List[str], environment: str):
        """Validate database configuration."""
        database_url = os.environ.get('DATABASE_URL', '')
        
        if environment == 'production':
            if not database_url:
                errors.append(
                    "❌ DATABASE_URL is required in production (use PostgreSQL)"
                )
            elif 'sqlite' in database_url.lower():
                warnings.append(
                    "⚠️  Using SQLite in production is not recommended - use PostgreSQL instead"
                )
    
    @classmethod
    def _validate_email_config(cls, warnings: List[str]):
        """Validate email configuration."""
        email_host = os.environ.get('EMAIL_HOST')
        email_user = os.environ.get('EMAIL_HOST_USER')
        email_password = os.environ.get('EMAIL_HOST_PASSWORD')
        
        if email_host and not (email_user and email_password):
            warnings.append(
                "⚠️  EMAIL_HOST is set but EMAIL_HOST_USER or EMAIL_HOST_PASSWORD is missing"
            )
    
    @classmethod
    def _validate_paystack_config(cls, warnings: List[str]):
        """Validate Paystack configuration."""
        public_key = os.environ.get('PAYSTACK_PUBLIC_KEY', '')
        secret_key = os.environ.get('PAYSTACK_SECRET_KEY', '')
        
        if public_key or secret_key:
            if not (public_key and secret_key):
                warnings.append(
                    "⚠️  Paystack configuration incomplete: both PUBLIC_KEY and SECRET_KEY are required"
                )
            
            # Check if using test keys in production
            django_env = os.environ.get('DJANGO_ENV', 'development')
            if django_env == 'production':
                if 'test' in public_key or 'test' in secret_key:
                    warnings.append(
                        "⚠️  Using Paystack TEST keys in production! Switch to LIVE keys."
                    )
    
    @classmethod
    def print_validation_report(cls, environment: str = 'development'):
        """Print a formatted validation report."""
        is_valid, errors, warnings = cls.validate_all(environment)
        
        print("\n" + "="*60)
        print(f"📋 Environment Validation Report ({environment.upper()})")
        print("="*60)
        
        if errors:
            print(f"\n❌ ERRORS ({len(errors)}):")
            for error in errors:
                print(f"  {error}")
        
        if warnings:
            print(f"\n⚠️  WARNINGS ({len(warnings)}):")
            for warning in warnings:
                print(f"  {warning}")
        
        if not errors and not warnings:
            print("\n✅ All environment variables are properly configured!")
        elif not errors:
            print("\n✅ Required variables are set (but there are warnings)")
        else:
            print("\n❌ Fix the errors above before running in production!")
        
        print("="*60 + "\n")
        
        return is_valid
    
    @classmethod
    def validate_or_exit(cls, environment: str = 'development'):
        """Validate environment and exit if errors found."""
        is_valid = cls.print_validation_report(environment)
        
        if not is_valid:
            logger.error("Environment validation failed. Fix the errors above and restart.")
            if environment == 'production':
                raise RuntimeError(
                    "Environment validation failed. Cannot start in production with missing required variables."
                )
        
        return is_valid


def validate_environment():
    """Convenience function to validate environment."""
    django_env = os.environ.get('DJANGO_ENV', 'development')
    return EnvironmentValidator.validate_or_exit(django_env)
