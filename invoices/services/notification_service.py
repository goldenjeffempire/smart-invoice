"""
NotificationService handles all notification delivery (email, WhatsApp, SMS).
Provides a centralized interface for sending invoices and payment reminders.
"""
from typing import Optional
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from twilio.rest import Client as TwilioClient
from ..utils import format_whatsapp_number
from ..exceptions import EmailDeliveryError, WhatsAppDeliveryError
import logging

logger = logging.getLogger(__name__)


class NotificationService:
    """
    Centralized service for handling all notification delivery.
    
    This service provides methods for sending invoices and payment reminders
    via email and WhatsApp, with proper error handling and logging.
    """
    
    @staticmethod
    def send_invoice_email(invoice, recipient_email: Optional[str] = None, pdf_bytes: Optional[bytes] = None) -> bool:
        """
        Send an invoice via email with optional PDF attachment.
        
        Args:
            invoice: The Invoice model instance to send.
            recipient_email: Optional recipient email. If not provided, uses invoice.client_email.
            pdf_bytes: Optional PDF file content as bytes. If provided, attached to email.
            
        Returns:
            True if email was sent successfully.
            
        Raises:
            EmailDeliveryError: If email delivery fails.
            ValueError: If no recipient email is available.
        """
        try:
            recipient = recipient_email or invoice.client_email
            if not recipient:
                raise ValueError("No recipient email provided")
            
            subject = f"Invoice {invoice.invoice_id} from {invoice.business_name}"
            
            html_message = render_to_string('invoices/emails/invoice_email.html', {
                'invoice': invoice,
                'business_name': invoice.business_name,
                'invoice_id': invoice.invoice_id,
            })
            
            email = EmailMessage(
                subject=subject,
                body=html_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[recipient],
            )
            email.content_subtype = 'html'
            
            if pdf_bytes:
                email.attach(
                    f'Invoice_{invoice.invoice_id}.pdf',
                    pdf_bytes,
                    'application/pdf'
                )
            
            email.send()
            logger.info(f"Invoice {invoice.invoice_id} sent successfully to {recipient}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending invoice email: {str(e)}")
            raise EmailDeliveryError(f"Failed to send invoice email: {str(e)}") from e
    
    @staticmethod
    def send_payment_reminder(invoice) -> bool:
        """
        Send a payment reminder email for an invoice.
        
        Args:
            invoice: The Invoice model instance for which to send a reminder.
            
        Returns:
            True if reminder was sent successfully.
            
        Raises:
            EmailDeliveryError: If email delivery fails.
            ValueError: If no client email is available.
        """
        try:
            if not invoice.client_email:
                raise ValueError("No client email available")
            
            subject = f"Payment Reminder: Invoice {invoice.invoice_id}"
            
            html_message = render_to_string('invoices/emails/payment_reminder.html', {
                'invoice': invoice,
            })
            
            email = EmailMessage(
                subject=subject,
                body=html_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[invoice.client_email],
            )
            email.content_subtype = 'html'
            email.send()
            
            logger.info(f"Payment reminder sent for invoice {invoice.invoice_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending payment reminder: {str(e)}")
            raise EmailDeliveryError(f"Failed to send payment reminder: {str(e)}") from e
    
    @staticmethod
    def send_whatsapp_message(phone_number: str, message: str) -> bool:
        """
        Send a WhatsApp message using Twilio.
        
        Args:
            phone_number: Recipient phone number (will be normalized to WhatsApp format).
            message: Message content to send.
            
        Returns:
            True if message was sent successfully.
            
        Raises:
            WhatsAppDeliveryError: If message delivery fails.
            ValueError: If Twilio credentials are not configured.
        """
        try:
            if not all([
                settings.TWILIO_ACCOUNT_SID,
                settings.TWILIO_AUTH_TOKEN,
                settings.TWILIO_WHATSAPP_NUMBER
            ]):
                raise ValueError("Twilio credentials not configured")
            
            client = TwilioClient(
                settings.TWILIO_ACCOUNT_SID,
                settings.TWILIO_AUTH_TOKEN
            )
            
            # Normalize phone number for WhatsApp
            phone_number = format_whatsapp_number(phone_number)
            
            twilio_message = client.messages.create(
                from_=settings.TWILIO_WHATSAPP_NUMBER,
                body=message,
                to=phone_number
            )
            
            logger.info(f"WhatsApp message sent to {phone_number}: {twilio_message.sid}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending WhatsApp message: {str(e)}")
            raise WhatsAppDeliveryError(f"Failed to send WhatsApp message: {str(e)}") from e
    
    @staticmethod
    def send_whatsapp_invoice(invoice, payment_link: Optional[str] = None) -> bool:
        """
        Send an invoice notification via WhatsApp.
        
        Args:
            invoice: The Invoice model instance to send.
            payment_link: Optional payment link to include in the message.
            
        Returns:
            True if invoice was sent successfully.
            
        Raises:
            WhatsAppDeliveryError: If WhatsApp delivery fails.
            ValueError: If no client phone number is available.
        """
        try:
            if not invoice.client_phone:
                raise ValueError("No client phone number available")
            
            message = f"""
Hi {invoice.client_name},

You have received a new invoice from {invoice.business_name}:

Invoice ID: {invoice.invoice_id}
Amount: {invoice.currency} {invoice.total_amount}
Due Date: {invoice.due_date}

{f'Pay now: {payment_link}' if payment_link else 'Please contact us for payment details.'}

Thank you for your business!
            """.strip()
            
            return NotificationService.send_whatsapp_message(
                invoice.client_phone,
                message
            )
            
        except Exception as e:
            logger.error(f"Error sending WhatsApp invoice: {str(e)}")
            raise WhatsAppDeliveryError(f"Failed to send WhatsApp invoice: {str(e)}") from e
