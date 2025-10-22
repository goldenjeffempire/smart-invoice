import requests
import json
import hmac
import hashlib
import logging
from decimal import Decimal
from django.conf import settings
from django.utils import timezone
from .models import Invoice, PaymentTransaction

logger = logging.getLogger(__name__)


class PaystackService:
    BASE_URL = 'https://api.paystack.co'
    
    def __init__(self):
        self.secret_key = settings.PAYSTACK_SECRET_KEY
        self.public_key = settings.PAYSTACK_PUBLIC_KEY
    
    def get_headers(self):
        return {
            'Authorization': f'Bearer {self.secret_key}',
            'Content-Type': 'application/json',
        }
    
    def initialize_transaction(self, invoice, callback_url):
        if not self.secret_key:
            raise ValueError('Paystack secret key is not configured')
        
        amount_in_kobo = int(invoice.total_amount * 100)
        
        reference = f"{invoice.invoice_id}-{timezone.now().strftime('%Y%m%d%H%M%S')}"
        
        payload = {
            'amount': amount_in_kobo,
            'email': invoice.client_email or 'customer@example.com',
            'reference': reference,
            'currency': invoice.currency,
            'callback_url': callback_url,
            'metadata': {
                'invoice_id': invoice.invoice_id,
                'business_name': invoice.business_name,
                'client_name': invoice.client_name,
                'custom_fields': [
                    {
                        'display_name': 'Invoice ID',
                        'variable_name': 'invoice_id',
                        'value': invoice.invoice_id
                    }
                ]
            }
        }
        
        try:
            response = requests.post(
                f'{self.BASE_URL}/transaction/initialize',
                headers=self.get_headers(),
                data=json.dumps(payload),
                timeout=10
            )
            
            response_data = response.json()
            
            if response.status_code == 200 and response_data.get('status'):
                data = response_data.get('data', {})
                
                payment_transaction = PaymentTransaction.objects.create(
                    invoice=invoice,
                    transaction_reference=reference,
                    payment_method='paystack',
                    amount=invoice.total_amount,
                    currency=invoice.currency,
                    status='pending',
                    payment_email=invoice.client_email or '',
                    paystack_response=response_data
                )
                
                invoice.paystack_reference = reference
                invoice.save()
                
                logger.info(f"Payment initialized for invoice {invoice.invoice_id}: {reference}")
                
                return {
                    'success': True,
                    'authorization_url': data.get('authorization_url'),
                    'access_code': data.get('access_code'),
                    'reference': reference
                }
            else:
                error_message = response_data.get('message', 'Unknown error occurred')
                logger.error(f"Paystack initialization failed for invoice {invoice.invoice_id}: {error_message}")
                return {
                    'success': False,
                    'message': error_message
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error during Paystack initialization: {str(e)}")
            return {
                'success': False,
                'message': f'Network error: {str(e)}'
            }
        except Exception as e:
            logger.error(f"Unexpected error during Paystack initialization: {str(e)}")
            return {
                'success': False,
                'message': f'System error: {str(e)}'
            }
    
    def verify_transaction(self, reference):
        if not self.secret_key:
            raise ValueError('Paystack secret key is not configured')
        
        try:
            response = requests.get(
                f'{self.BASE_URL}/transaction/verify/{reference}',
                headers=self.get_headers(),
                timeout=10
            )
            
            response_data = response.json()
            
            if response.status_code == 200 and response_data.get('status'):
                data = response_data.get('data', {})
                
                logger.info(f"Transaction verification successful for reference: {reference}")
                
                return {
                    'success': True,
                    'data': data,
                    'status': data.get('status'),
                    'amount': Decimal(data.get('amount', 0)) / 100,
                    'currency': data.get('currency'),
                    'paid_at': data.get('paid_at'),
                    'customer': data.get('customer', {})
                }
            else:
                error_message = response_data.get('message', 'Verification failed')
                logger.error(f"Transaction verification failed for {reference}: {error_message}")
                return {
                    'success': False,
                    'message': error_message
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error during transaction verification: {str(e)}")
            return {
                'success': False,
                'message': f'Network error: {str(e)}'
            }
        except Exception as e:
            logger.error(f"Unexpected error during transaction verification: {str(e)}")
            return {
                'success': False,
                'message': f'System error: {str(e)}'
            }
    
    def verify_webhook_signature(self, payload, signature):
        if not self.secret_key:
            return False
        
        hash_value = hmac.new(
            self.secret_key.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha512
        ).hexdigest()
        
        return hash_value == signature
    
    def process_payment_success(self, payment_data):
        from django.db import transaction as db_transaction
        
        reference = payment_data.get('reference')
        
        try:
            with db_transaction.atomic():
                try:
                    payment_transaction = PaymentTransaction.objects.select_for_update().get(
                        transaction_reference=reference
                    )
                except PaymentTransaction.DoesNotExist:
                    try:
                        invoice = Invoice.objects.get(paystack_reference=reference)
                        payment_transaction = PaymentTransaction.objects.create(
                            invoice=invoice,
                            transaction_reference=reference,
                            payment_method='paystack',
                            amount=invoice.total_amount,
                            currency=invoice.currency,
                            status='pending',
                            payment_email=invoice.client_email or ''
                        )
                        logger.info(f"Created missing payment transaction for reference: {reference}")
                    except Invoice.DoesNotExist:
                        logger.error(f"No invoice or payment transaction found for reference: {reference}")
                        return {
                            'success': False,
                            'message': 'Invoice not found'
                        }
                
                if payment_transaction.status == 'successful':
                    logger.info(f"Payment already processed for reference: {reference}")
                    return {
                        'success': True,
                        'invoice': payment_transaction.invoice,
                        'payment': payment_transaction
                    }
                
                invoice = payment_transaction.invoice
                
                payment_transaction.status = 'successful'
                payment_transaction.payment_date = timezone.now()
                payment_transaction.paystack_response = payment_data
                payment_transaction.paid_by = payment_data.get('customer', {}).get('email', '')
                payment_transaction.save()
                
                invoice.status = 'paid'
                invoice.paid_date = timezone.now().date()
                invoice.save()
                
                logger.info(f"Payment processed successfully for invoice {invoice.invoice_id}")
                
                return {
                    'success': True,
                    'invoice': invoice,
                    'payment': payment_transaction
                }
            
        except Exception as e:
            logger.error(f"Error processing payment success: {str(e)}")
            return {
                'success': False,
                'message': str(e)
            }
    
    def process_payment_failure(self, payment_data):
        from django.db import transaction as db_transaction
        
        reference = payment_data.get('reference')
        
        try:
            with db_transaction.atomic():
                try:
                    payment_transaction = PaymentTransaction.objects.select_for_update().get(
                        transaction_reference=reference
                    )
                except PaymentTransaction.DoesNotExist:
                    try:
                        invoice = Invoice.objects.get(paystack_reference=reference)
                        payment_transaction = PaymentTransaction.objects.create(
                            invoice=invoice,
                            transaction_reference=reference,
                            payment_method='paystack',
                            amount=invoice.total_amount,
                            currency=invoice.currency,
                            status='pending',
                            payment_email=invoice.client_email or ''
                        )
                    except Invoice.DoesNotExist:
                        logger.error(f"No invoice or payment transaction found for failed payment: {reference}")
                        return {
                            'success': False,
                            'message': 'Invoice not found'
                        }
                
                payment_transaction.status = 'failed'
                payment_transaction.paystack_response = payment_data
                payment_transaction.notes = payment_data.get('gateway_response', 'Payment failed')
                payment_transaction.save()
                
                logger.warning(f"Payment failed for reference: {reference}")
                
                return {
                    'success': True,
                    'payment': payment_transaction
                }
            
        except Exception as e:
            logger.error(f"Error processing payment failure: {str(e)}")
            return {
                'success': False,
                'message': str(e)
            }
