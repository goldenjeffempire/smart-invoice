# invoices/models.py
from django.db import models
from django.utils import timezone
import uuid

CURRENCY_CHOICES = [
    ('NGN', 'Naira (NGN)'),
    ('USD', 'US Dollar (USD)'),
    ('GBP', 'British Pound (GBP)'),
]

class Invoice(models.Model):
    invoice_id = models.CharField(max_length=32, unique=True, editable=False)
    created_at = models.DateTimeField(default=timezone.now)
    business_name = models.CharField(max_length=200)
    client_name = models.CharField(max_length=200)
    client_email_or_whatsapp = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='NGN')
    notes = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if not self.invoice_id:
            self.invoice_id = f"ONM-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.invoice_id} — {self.business_name} → {self.client_name}"
