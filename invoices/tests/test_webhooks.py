"""
Unit tests for Paystack webhook handling.
Tests webhook signature verification, idempotency, and event processing.
"""
import pytest
import json
import hmac
import hashlib
from decimal import Decimal
from django.test import TestCase, Client as TestClient
from django.contrib.auth.models import User
from django.urls import reverse
from django.conf import settings

from invoices.models import Invoice, PaymentTransaction, Client


@pytest.mark.django_db
class TestPaystackWebhook(TestCase):
    """Test Paystack webhook endpoint."""
    
    def setUp(self):
        """Set up test data."""
        self.client_http = TestClient()
        
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.client_obj = Client.objects.create(
            user=self.user,
            name='Test Client',
            email='client@example.com'
        )
        
        self.invoice = Invoice.objects.create(
            user=self.user,
            client=self.client_obj,
            business_name='Test Business',
            client_name='Test Client',
            client_email='client@example.com',
            description='Test Service',
            quantity=Decimal('1.00'),
            unit_price=Decimal('1000.00'),
            currency='NGN',
            status='sent',
            paystack_reference='test_ref_123'
        )
        
        self.payment_transaction = PaymentTransaction.objects.create(
            invoice=self.invoice,
            transaction_reference='test_ref_123',
            payment_method='paystack',
            amount=self.invoice.total_amount,
            currency=self.invoice.currency,
            status='pending'
        )
    
    def generate_webhook_signature(self, payload_dict):
        """Generate valid webhook signature."""
        payload_str = json.dumps(payload_dict)
        secret = settings.PAYSTACK_WEBHOOK_SECRET or settings.PAYSTACK_SECRET_KEY
        signature = hmac.new(
            secret.encode('utf-8'),
            payload_str.encode('utf-8'),
            hashlib.sha512
        ).hexdigest()
        return payload_str, signature
    
    def test_webhook_without_signature(self):
        """Test webhook request without signature is rejected."""
        url = reverse('paystack_webhook')
        response = self.client_http.post(
            url,
            data=json.dumps({'event': 'charge.success'}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('No signature', response.json()['error'])
    
    def test_webhook_with_invalid_signature(self):
        """Test webhook request with invalid signature is rejected."""
        payload = {'event': 'charge.success'}
        url = reverse('paystack_webhook')
        
        response = self.client_http.post(
            url,
            data=json.dumps(payload),
            content_type='application/json',
            HTTP_X_PAYSTACK_SIGNATURE='invalid_signature'
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid signature', response.json()['error'])
    
    def test_webhook_charge_success(self):
        """Test successful charge webhook."""
        payload = {
            'event': 'charge.success',
            'data': {
                'reference': 'test_ref_123',
                'amount': 100000,
                'currency': 'NGN',
                'customer': {'email': 'client@example.com'}
            }
        }
        
        payload_str, signature = self.generate_webhook_signature(payload)
        url = reverse('paystack_webhook')
        
        response = self.client_http.post(
            url,
            data=payload_str,
            content_type='application/json',
            HTTP_X_PAYSTACK_SIGNATURE=signature
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')
        
        self.payment_transaction.refresh_from_db()
        self.assertEqual(self.payment_transaction.status, 'successful')
        
        self.invoice.refresh_from_db()
        self.assertEqual(self.invoice.status, 'paid')
    
    def test_webhook_charge_success_idempotency(self):
        """Test that duplicate webhooks are handled idempotently."""
        self.payment_transaction.status = 'successful'
        self.payment_transaction.save()
        
        payload = {
            'event': 'charge.success',
            'data': {
                'reference': 'test_ref_123',
                'amount': 100000,
                'currency': 'NGN'
            }
        }
        
        payload_str, signature = self.generate_webhook_signature(payload)
        url = reverse('paystack_webhook')
        
        response = self.client_http.post(
            url,
            data=payload_str,
            content_type='application/json',
            HTTP_X_PAYSTACK_SIGNATURE=signature
        )
        
        self.assertEqual(response.status_code, 200)
        
        self.payment_transaction.refresh_from_db()
        self.assertEqual(self.payment_transaction.status, 'successful')
    
    def test_webhook_charge_failed(self):
        """Test failed charge webhook."""
        payload = {
            'event': 'charge.failed',
            'data': {
                'reference': 'test_ref_123',
                'gateway_response': 'Declined by bank'
            }
        }
        
        payload_str, signature = self.generate_webhook_signature(payload)
        url = reverse('paystack_webhook')
        
        response = self.client_http.post(
            url,
            data=payload_str,
            content_type='application/json',
            HTTP_X_PAYSTACK_SIGNATURE=signature
        )
        
        self.assertEqual(response.status_code, 200)
        
        self.payment_transaction.refresh_from_db()
        self.assertEqual(self.payment_transaction.status, 'failed')
    
    def test_webhook_invalid_json(self):
        """Test webhook with invalid JSON payload."""
        url = reverse('paystack_webhook')
        
        response = self.client_http.post(
            url,
            data='invalid json',
            content_type='application/json',
            HTTP_X_PAYSTACK_SIGNATURE='dummy_signature'
        )
        
        self.assertEqual(response.status_code, 400)
