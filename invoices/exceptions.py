"""
Custom exception classes for the invoices app.
Provides better error handling and user feedback.
"""


class InvoiceError(Exception):
    """Base exception for invoice-related errors."""
    pass


class InvoiceNotFoundError(InvoiceError):
    """Raised when an invoice cannot be found."""
    pass


class InvalidInvoiceDataError(InvoiceError):
    """Raised when invoice data is invalid or incomplete."""
    pass


class PaymentError(Exception):
    """Base exception for payment-related errors."""
    pass


class PaymentProcessingError(PaymentError):
    """Raised when payment processing fails."""
    pass


class PaymentVerificationError(PaymentError):
    """Raised when payment verification fails."""
    pass


class WebhookError(Exception):
    """Base exception for webhook-related errors."""
    pass


class InvalidWebhookSignatureError(WebhookError):
    """Raised when webhook signature validation fails."""
    pass


class NotificationError(Exception):
    """Base exception for notification-related errors."""
    pass


class EmailDeliveryError(NotificationError):
    """Raised when email delivery fails."""
    pass


class WhatsAppDeliveryError(NotificationError):
    """Raised when WhatsApp message delivery fails."""
    pass


class PDFGenerationError(InvoiceError):
    """Raised when PDF generation fails."""
    pass


class StorageError(Exception):
    """Base exception for storage-related errors."""
    pass


class CloudStorageError(StorageError):
    """Raised when cloud storage operations fail."""
    pass
