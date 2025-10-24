# invoices/models.py
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from decimal import Decimal
import uuid

CURRENCY_CHOICES = [
    ('USD', 'US Dollar (USD)'),
    ('EUR', 'Euro (EUR)'),
    ('GBP', 'British Pound (GBP)'),
    ('NGN', 'Naira (NGN)'),
    ('CAD', 'Canadian Dollar (CAD)'),
    ('AUD', 'Australian Dollar (AUD)'),
]

STATUS_CHOICES = [
    ('draft', 'Draft'),
    ('sent', 'Sent'),
    ('paid', 'Paid'),
    ('overdue', 'Overdue'),
    ('cancelled', 'Cancelled'),
]

PAYMENT_TERMS_CHOICES = [
    ('immediate', 'Due Immediately'),
    ('net_15', 'Net 15 Days'),
    ('net_30', 'Net 30 Days'),
    ('net_60', 'Net 60 Days'),
    ('net_90', 'Net 90 Days'),
]

class SupportInquiry(models.Model):
    name = models.CharField(max_length=200, verbose_name="Name")
    email = models.EmailField(verbose_name="Email")
    subject = models.CharField(max_length=300, verbose_name="Subject")
    message = models.TextField(verbose_name="Message")
    created_at = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Support Inquiry"
        verbose_name_plural = "Support Inquiries"
    
    def __str__(self):
        return f"{self.subject} - {self.email}"


PAYMENT_STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('successful', 'Successful'),
    ('failed', 'Failed'),
    ('cancelled', 'Cancelled'),
]

PAYMENT_METHOD_CHOICES = [
    ('paystack', 'Paystack'),
    ('bank_transfer', 'Bank Transfer'),
    ('cash', 'Cash'),
    ('other', 'Other'),
]


class Client(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='clients')
    name = models.CharField(max_length=200, verbose_name="Client Name")
    email = models.EmailField(max_length=200, blank=True, verbose_name="Email")
    phone = models.CharField(max_length=50, blank=True, verbose_name="Phone/WhatsApp")
    address = models.TextField(blank=True, verbose_name="Address")
    company_name = models.CharField(max_length=200, blank=True, verbose_name="Company Name")
    tax_id = models.CharField(max_length=100, blank=True, verbose_name="Tax ID/VAT Number")
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    notes = models.TextField(blank=True, verbose_name="Notes")
    
    class Meta:
        ordering = ['name']
        verbose_name = "Client"
        verbose_name_plural = "Clients"
        indexes = [
            models.Index(fields=['user', 'name']),
            models.Index(fields=['email']),
        ]
        unique_together = ['user', 'email']
    
    def __str__(self):
        return f"{self.name} ({self.email})" if self.email else self.name
    
    @property
    def total_invoices(self):
        return self.invoices.count()
    
    @property
    def total_revenue(self):
        return self.invoices.filter(status='paid').aggregate(total=models.Sum('total_amount'))['total'] or Decimal('0.00')


class PaymentTransaction(models.Model):
    invoice = models.ForeignKey('Invoice', on_delete=models.CASCADE, related_name='payments')
    transaction_reference = models.CharField(max_length=200, unique=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='paystack')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    
    paystack_response = models.JSONField(blank=True, null=True)
    payment_date = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    paid_by = models.CharField(max_length=200, blank=True)
    payment_email = models.EmailField(blank=True)
    payment_phone = models.CharField(max_length=50, blank=True)
    
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Payment Transaction"
        verbose_name_plural = "Payment Transactions"
        indexes = [
            models.Index(fields=['transaction_reference']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['invoice', 'status']),
        ]
    
    def __str__(self):
        return f"{self.transaction_reference} - {self.status} - {self.currency} {self.amount}"


class Invoice(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invoices', null=True, blank=True)
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, related_name='invoices', null=True, blank=True)
    invoice_id = models.CharField(max_length=32, unique=True, editable=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    business_name = models.CharField(max_length=200, verbose_name="Business Name")
    business_email = models.EmailField(max_length=200, blank=True, verbose_name="Business Email")
    business_address = models.TextField(blank=True, verbose_name="Business Address")
    business_phone = models.CharField(max_length=50, blank=True, verbose_name="Business Phone")
    business_logo_url = models.URLField(max_length=500, blank=True, verbose_name="Business Logo URL")
    
    client_name = models.CharField(max_length=200, verbose_name="Client Name")
    client_email = models.EmailField(max_length=200, blank=True, verbose_name="Client Email")
    client_phone = models.CharField(max_length=50, blank=True, verbose_name="Client Phone/WhatsApp")
    client_address = models.TextField(blank=True, verbose_name="Client Address")
    
    description = models.TextField(default='', verbose_name="Service/Product Description")
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1, verbose_name="Quantity")
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Unit Price")
    
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, editable=False, default=0)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Tax Rate (%)")
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, editable=False, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Discount Amount")
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, editable=False, default=0)
    
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='USD')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    payment_terms = models.CharField(max_length=20, choices=PAYMENT_TERMS_CHOICES, default='net_30')
    
    issue_date = models.DateField(default=timezone.now, verbose_name="Issue Date")
    due_date = models.DateField(blank=True, null=True, verbose_name="Due Date")
    paid_date = models.DateField(blank=True, null=True, verbose_name="Date Paid")
    
    notes = models.TextField(blank=True, verbose_name="Additional Notes")
    payment_instructions = models.TextField(blank=True, verbose_name="Payment Instructions")
    paystack_reference = models.CharField(max_length=100, blank=True, null=True, verbose_name="Paystack Reference")
    
    def save(self, *args, **kwargs):
        if not self.invoice_id:
            self.invoice_id = f"INV-{uuid.uuid4().hex[:8].upper()}"
        
        self.subtotal = self.quantity * self.unit_price
        self.tax_amount = (self.subtotal * self.tax_rate) / Decimal('100')
        self.total_amount = self.subtotal + self.tax_amount - self.discount_amount
        
        if self.due_date and self.status == 'sent':
            if timezone.now().date() > self.due_date and self.status != 'paid':
                self.status = 'overdue'
        
        super().save(*args, **kwargs)
    
    @property
    def is_overdue(self):
        if self.due_date and self.status not in ['paid', 'cancelled']:
            return timezone.now().date() > self.due_date
        return False
    
    @property
    def days_until_due(self):
        if self.due_date:
            delta = self.due_date - timezone.now().date()
            return delta.days
        return None
    
    def __str__(self):
        return f"{self.invoice_id} — {self.business_name} → {self.client_name} ({self.get_status_display()})"
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Invoice"
        verbose_name_plural = "Invoices"
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['status', 'due_date']),
            models.Index(fields=['invoice_id']),
            models.Index(fields=['created_at']),
            models.Index(fields=['paystack_reference']),
            models.Index(fields=['client']),
        ]


class InvoiceLineItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='line_items')
    description = models.TextField(verbose_name="Item Description")
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1, verbose_name="Quantity")
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Unit Price")
    amount = models.DecimalField(max_digits=12, decimal_places=2, editable=False)
    
    created_at = models.DateTimeField(default=timezone.now)
    order = models.IntegerField(default=0, verbose_name="Display Order")
    
    def save(self, *args, **kwargs):
        self.amount = self.quantity * self.unit_price
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['order', 'id']
        verbose_name = "Invoice Line Item"
        verbose_name_plural = "Invoice Line Items"
    
    def __str__(self):
        return f"{self.description[:50]} - {self.quantity} x {self.unit_price}"
