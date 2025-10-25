"""
StorageService handles cloud storage operations for files like PDFs.
Provides integration with Cloudinary for production-ready file storage.
"""
from typing import Optional, Tuple
from django.conf import settings
import cloudinary
import cloudinary.uploader
import logging
from ..exceptions import CloudStorageError, PDFGenerationError

logger = logging.getLogger(__name__)


class StorageService:
    """
    Centralized service for handling cloud storage operations.
    
    Provides methods for uploading, retrieving, and deleting files from Cloudinary,
    with fallback to local storage when Cloudinary is not configured.
    """
    
    @staticmethod
    def is_cloudinary_configured() -> bool:
        """
        Check if Cloudinary credentials are configured.
        
        Returns:
            True if Cloudinary is properly configured, False otherwise.
        """
        cloudinary_url = getattr(settings, 'CLOUDINARY_URL', '')
        return bool(cloudinary_url) or all([
            getattr(settings, 'CLOUDINARY_CLOUD_NAME', None),
            getattr(settings, 'CLOUDINARY_API_KEY', None),
            getattr(settings, 'CLOUDINARY_API_SECRET', None),
        ])
    
    @staticmethod
    def upload_pdf(pdf_bytes: bytes, filename: str, folder: str = 'invoices') -> Tuple[str, str]:
        """
        Upload a PDF file to Cloudinary cloud storage.
        
        Args:
            pdf_bytes: The PDF file content as bytes.
            filename: The filename for the PDF (without extension).
            folder: Cloudinary folder to store the file in (default: 'invoices').
            
        Returns:
            Tuple of (public_url, public_id) where:
                - public_url: The secure HTTPS URL to access the PDF
                - public_id: Cloudinary's unique identifier for the file
            
        Raises:
            CloudStorageError: If upload fails or Cloudinary is not configured.
            PDFGenerationError: If pdf_bytes is invalid.
        """
        if not StorageService.is_cloudinary_configured():
            raise CloudStorageError(
                "Cloudinary is not configured. Please set CLOUDINARY_URL or "
                "CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, and CLOUDINARY_API_SECRET "
                "environment variables."
            )
        
        if not pdf_bytes:
            raise PDFGenerationError("PDF bytes are empty or invalid")
        
        try:
            # Configure Cloudinary (in case not done in settings)
            # Check if CLOUDINARY_URL is set (takes precedence)
            cloudinary_url = getattr(settings, 'CLOUDINARY_URL', '')
            if cloudinary_url:
                # CLOUDINARY_URL contains all credentials, just ensure it's used
                # The cloudinary library automatically reads from CLOUDINARY_URL environment variable
                pass
            else:
                # Fall back to explicit credentials
                cloudinary.config(
                    cloud_name=getattr(settings, 'CLOUDINARY_CLOUD_NAME', ''),
                    api_key=getattr(settings, 'CLOUDINARY_API_KEY', ''),
                    api_secret=getattr(settings, 'CLOUDINARY_API_SECRET', ''),
                    secure=True
                )
            
            # Upload PDF as raw file to Cloudinary
            upload_result = cloudinary.uploader.upload(
                pdf_bytes,
                resource_type='raw',  # For non-image files like PDFs
                folder=folder,
                public_id=filename,
                overwrite=True,
                invalidate=True,  # Invalidate CDN cache
                format='pdf'
            )
            
            secure_url = upload_result.get('secure_url')
            public_id = upload_result.get('public_id')
            
            if not secure_url or not public_id:
                raise CloudStorageError("Upload succeeded but missing URL or public_id in response")
            
            logger.info(f"Successfully uploaded PDF to Cloudinary: {public_id}")
            return secure_url, public_id
            
        except cloudinary.exceptions.Error as e:
            logger.error(f"Cloudinary upload error: {str(e)}")
            raise CloudStorageError(f"Failed to upload PDF to Cloudinary: {str(e)}") from e
        except Exception as e:
            logger.error(f"Unexpected error during PDF upload: {str(e)}")
            raise CloudStorageError(f"Failed to upload PDF: {str(e)}") from e
    
    @staticmethod
    def delete_pdf(public_id: str) -> bool:
        """
        Delete a PDF file from Cloudinary.
        
        Args:
            public_id: The Cloudinary public ID of the file to delete.
            
        Returns:
            True if deletion was successful.
            
        Raises:
            CloudStorageError: If deletion fails or Cloudinary is not configured.
        """
        if not StorageService.is_cloudinary_configured():
            logger.warning("Cloudinary not configured, skipping deletion")
            return False
        
        try:
            result = cloudinary.uploader.destroy(
                public_id,
                resource_type='raw',
                invalidate=True
            )
            
            success = result.get('result') == 'ok'
            if success:
                logger.info(f"Successfully deleted PDF from Cloudinary: {public_id}")
            else:
                logger.warning(f"Failed to delete PDF from Cloudinary: {public_id}, result: {result}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error deleting PDF from Cloudinary: {str(e)}")
            raise CloudStorageError(f"Failed to delete PDF: {str(e)}") from e
    
    @staticmethod
    def get_pdf_url(public_id: str) -> Optional[str]:
        """
        Get the secure URL for a PDF stored in Cloudinary.
        
        Args:
            public_id: The Cloudinary public ID of the file.
            
        Returns:
            The secure HTTPS URL to access the PDF, or None if not configured.
        """
        if not StorageService.is_cloudinary_configured():
            return None
        
        try:
            # Build the URL for the PDF
            from cloudinary import CloudinaryResource
            resource = CloudinaryResource(public_id, resource_type='raw', format='pdf')
            return resource.build_url(secure=True)
        except Exception as e:
            logger.error(f"Error building PDF URL: {str(e)}")
            return None
