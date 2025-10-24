"""
Unit tests for Paystack payment service.
Tests payment initialization, verification, and webhook handling.
"""
import pytest
import json
import hmac
import hashlib
from decimal import Decimal
from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone

from invoices.models import Invoice, PaymentTransaction, Client
from invoices.payment_service import PaystackService


@pytest.mark.django_db
class TestPaystackService(TestCase):
    """Test Paystack payment service functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.client = Client.objects.create(
            user=self.user,
            name='Test Client',
            email='client@example.com',
            phone='+2348012345678'
        )
        
        self.invoice = Invoice.objects.create(
            user=self.user,
            client=self.client,
            business_name='Test Business',
            business_email='business@example.com',
            client_name='Test Client',
            client_email='client@example.com',
            description='Test Service',
            quantity=Decimal('1.00'),
            unit_price=Decimal('1000.00'),
            currency='NGN',
            status='sent'
        )
    
    @patch('invoices.payment_service.requests.post')
    def test_initialize_transaction_success(self, mock_post):
        """Test successful payment initialization."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'status': True,
            'data': {
                'authorization_url': 'https://checkout.paystack.com/test123',
                'access_code': 'test_access_code',
                'reference': 'test_ref_123'
            }
        }
        mock_post.return_value = mock_response
        
        service = PaystackService()
        result = service.initialize_transaction(self.invoice, 'http://localhost/callback')
        
        self.assertTrue(result['success'])
        self.assertEqual(result['authorization_url'], 'https://checkout.paystack.com/test123')
        self.assertIn('reference', result)
        
        payment = PaymentTransaction.objects.get(invoice=self.invoice)
        self.assertEqual(payment.status, 'pending')
        self.assertEqual(payment.amount, self.invoice.total_amount)
    
    @patch('invoices.payment_service.requests.post')
    def test_initialize_transaction_failure(self, mock_post):
        """Test payment initialization failure."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            'status': False,
            'message': 'Invalid parameters'
        }
        mock_post.return_value = mock_response
        
        service = PaystackService()
        result = service.initialize_transaction(self.invoice, 'http://localhost/callback')
        
        self.assertFalse(result['success'])
        self.assertIn('message', result)
    
    @patch('invoices.payment_service.requests.get')
    def test_verify_transaction_success(self, mock_get):
        """Test successful transaction verification."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'status': True,
            'data': {
                'status': 'success',
                'amount': 100000,
                'currency': 'NGN',
                'paid_at': '2025-10-24T10:00:00.000Z',
                'customer': {'email': 'client@example.com'}
            }
        }
        mock_get.return_value = mock_response
        
        service = PaystackService()
        result = service.verify_transaction('test_ref_123')
        
        self.assertTrue(result['success'])
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['amount'], Decimal('1000.00'))
    
    def test_verify_webhook_signature(self):
        """Test webhook signature verification."""
        service = PaystackService()
        service.webhook_secret = 'test_secret_key'
        
        payload = json.dumps({'event': 'charge.success'})
        signature = hmac.new(
            service.webhook_secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha512
        ).hexdigest()
        
        self.assertTrue(service.verify_webhook_signature(payload, signature))
        
        invalid_signature = 'invalid_signature_hash'
        self.assertFalse(service.verify_webhook_signature(payload, invalid_signature))
    
    def test_process_payment_success(self):
        """Test processing successful payment."""
        payment_transaction = PaymentTransaction.objects.create(
            invoice=self.invoice,
            transaction_reference='test_ref_123',
            payment_method='paystack',
            amount=self.invoice.total_amount,
            currency=self.invoice.currency,
            status='pending'
        )
        
        payment_data = {
            'reference': 'test_ref_123',
            'amount': 100000,
            'currency': 'NGN',
            'customer': {'email': 'client@example.com'}
        }
        
        service = PaystackService()
        result = service.process_payment_success(payment_data)
        
        self.assertTrue(result['success'])
        
        payment_transaction.refresh_from_db()
        self.assertEqual(payment_transaction.status, 'successful')
        
        self.invoice.refresh_from_db()
        self.assertEqual(self.invoice.status, 'paid')
        self.assertIsNotNone(self.invoice.paid_date)
    
    def test_process_payment_success_idempotency(self):
        """Test that processing the same payment twice is idempotent."""
        payment_transaction = PaymentTransaction.objects.create(
            invoice=self.invoice,
            transaction_reference='test_ref_123',
            payment_method='paystack',
            amount=self.invoice.total_amount,
            currency=self.invoice.currency,
            status='successful',
            payment_date=timezone.now()
        )
        
        payment_data = {
            'reference': 'test_ref_123',
            'amount': 100000,
            'currency': 'NGN'
        }
        
        service = PaystackService()
        result = service.process_payment_success(payment_data)
        
        self.assertTrue(result['success'])
        
        payment_transaction.refresh_from_db()
        self.assertEqual(payment_transaction.status, 'successful')
    
    def test_process_payment_failure(self):
        """Test processing failed payment."""
        payment_transaction = PaymentTransaction.objects.create(
            invoice=self.invoice,
            transaction_reference='test_ref_456',
            payment_method='paystack',
            amount=self.invoice.total_amount,
            currency=self.invoice.currency,
            status='pending'
        )
        
        payment_data = {
            'reference': 'test_ref_456',
            'gateway_response': 'Declined by bank'
        }
        
        service = PaystackService()
        result = service.process_payment_failure(payment_data)
        
        self.assertTrue(result['success'])
        
        payment_transaction.refresh_from_db()
        self.assertEqual(payment_transaction.status, 'failed')
        self.assertIn('Declined', payment_transaction.notes)
