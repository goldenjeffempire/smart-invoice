"""
Unit tests for API endpoints.
Tests Paystack checkout creation API.
"""
import pytest
from decimal import Decimal
from unittest.mock import patch, Mock
from django.test import TestCase, Client as TestClient
from django.contrib.auth.models import User
from django.urls import reverse

from invoices.models import Invoice, Client


@pytest.mark.django_db
class TestPaystackCheckoutAPI(TestCase):
    """Test create Paystack checkout API endpoint."""
    
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
            status='sent'
        )
    
    def test_create_checkout_get_method_not_allowed(self):
        """Test that GET requests are not allowed."""
        url = reverse('create_paystack_checkout', args=[self.invoice.pk])
        response = self.client_http.get(url)
        
        self.assertEqual(response.status_code, 405)
        self.assertIn('Method not allowed', response.json()['error'])
    
    @patch('invoices.views.PaystackService')
    def test_create_checkout_success(self, mock_paystack_service):
        """Test successful checkout creation."""
        mock_service = Mock()
        mock_service.initialize_transaction.return_value = {
            'success': True,
            'authorization_url': 'https://checkout.paystack.com/test123',
            'reference': 'test_ref_123'
        }
        mock_paystack_service.return_value = mock_service
        
        url = reverse('create_paystack_checkout', args=[self.invoice.pk])
        response = self.client_http.post(url)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertTrue(data['success'])
        self.assertEqual(data['checkout_url'], 'https://checkout.paystack.com/test123')
        self.assertEqual(data['reference'], 'test_ref_123')
        self.assertEqual(data['invoice_id'], self.invoice.invoice_id)
        self.assertEqual(data['amount'], float(self.invoice.total_amount))
    
    @patch('invoices.views.PaystackService')
    def test_create_checkout_failure(self, mock_paystack_service):
        """Test checkout creation failure."""
        mock_service = Mock()
        mock_service.initialize_transaction.return_value = {
            'success': False,
            'message': 'Paystack API error'
        }
        mock_paystack_service.return_value = mock_service
        
        url = reverse('create_paystack_checkout', args=[self.invoice.pk])
        response = self.client_http.post(url)
        
        self.assertEqual(response.status_code, 500)
        data = response.json()
        
        self.assertFalse(data['success'])
        self.assertIn('error', data)
    
    def test_create_checkout_invalid_invoice(self):
        """Test checkout creation with invalid invoice ID."""
        url = reverse('create_paystack_checkout', args=[99999])
        response = self.client_http.post(url)
        
        self.assertEqual(response.status_code, 404)
        self.assertIn('Invoice not found', response.json()['error'])
