from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import secrets


class Invoice(models.Model):
    CURRENCY_CHOICES = [
        ("USD", "US Dollar"),
        ("EUR", "Euro"),
        ("GBP", "British Pound"),
        ("NGN", "Nigerian Naira"),
        ("CAD", "Canadian Dollar"),
        ("AUD", "Australian Dollar"),
    ]

    STATUS_CHOICES = [
        ("unpaid", "Unpaid"),
        ("paid", "Paid"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="invoices")
    invoice_id = models.CharField(max_length=20, unique=True, editable=False)

    business_name = models.CharField(max_length=200)
    business_email = models.EmailField()
    business_phone = models.CharField(max_length=50, blank=True)
    business_address = models.TextField()

    client_name = models.CharField(max_length=200)
    client_email = models.EmailField()
    client_phone = models.CharField(max_length=50, blank=True)
    client_address = models.TextField()

    invoice_date = models.DateField(default=timezone.now)
    due_date = models.DateField(null=True, blank=True)

    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default="USD")
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    brand_name = models.CharField(max_length=100, blank=True)
    brand_color = models.CharField(max_length=7, default="#6366f1")
    logo = models.ImageField(upload_to="logos/", null=True, blank=True)

    bank_name = models.CharField(max_length=200, blank=True)
    account_name = models.CharField(max_length=200, blank=True)
    account_number = models.CharField(max_length=100, blank=True)

    notes = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="unpaid")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.invoice_id:
            self.invoice_id = self.generate_invoice_id()
        super().save(*args, **kwargs)

    def generate_invoice_id(self):
        prefix = "INV"
        random_part = secrets.token_hex(3).upper()
        invoice_id = f"{prefix}{random_part}"

        while Invoice.objects.filter(invoice_id=invoice_id).exists():
            random_part = secrets.token_hex(3).upper()
            invoice_id = f"{prefix}{random_part}"

        return invoice_id

    @property
    def subtotal(self):
        return sum(item.total for item in self.line_items.all())

    @property
    def tax_amount(self):
        return (self.subtotal * self.tax_rate) / 100

    @property
    def total(self):
        return self.subtotal + self.tax_amount

    def __str__(self):
        return f"{self.invoice_id} - {self.client_name}"

    class Meta:
        ordering = ["-created_at"]


class LineItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="line_items")
    description = models.CharField(max_length=500)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def total(self):
        return self.quantity * self.unit_price

    def __str__(self):
        return f"{self.description} - {self.invoice.invoice_id}"
