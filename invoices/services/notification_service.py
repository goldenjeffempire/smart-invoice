from typing import Optional
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from twilio.rest import Client as TwilioClient
import logging

logger = logging.getLogger(__name__)


class NotificationService:
    
    @staticmethod
    def send_invoice_email(invoice, recipient_email: Optional[str] = None, pdf_bytes: Optional[bytes] = None):
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
            raise
    
    @staticmethod
    def send_payment_reminder(invoice):
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
            raise
    
    @staticmethod
    def send_whatsapp_message(phone_number: str, message: str):
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
            
            if not phone_number.startswith('whatsapp:'):
                phone_number = f'whatsapp:{phone_number}'
            
            message = client.messages.create(
                from_=settings.TWILIO_WHATSAPP_NUMBER,
                body=message,
                to=phone_number
            )
            
            logger.info(f"WhatsApp message sent to {phone_number}: {message.sid}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending WhatsApp message: {str(e)}")
            raise
    
    @staticmethod
    def send_whatsapp_invoice(invoice, payment_link: Optional[str] = None):
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
            raise
