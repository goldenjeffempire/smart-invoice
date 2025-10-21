# invoices/admin.py
from django.contrib import admin
from .models import Invoice

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_id','business_name','client_name','amount','currency','created_at')
    readonly_fields = ('invoice_id','created_at')
