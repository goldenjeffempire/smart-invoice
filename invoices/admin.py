# invoices/admin.py
from django.contrib import admin
from .models import Invoice

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        'invoice_id', 'business_name', 'client_name', 'total_amount', 
        'currency', 'status', 'issue_date', 'due_date', 'created_at'
    )
    list_filter = ('status', 'currency', 'payment_terms', 'issue_date', 'created_at')
    search_fields = ('invoice_id', 'business_name', 'client_name', 'client_email', 'description')
    readonly_fields = ('invoice_id', 'created_at', 'updated_at', 'subtotal', 'tax_amount', 'total_amount')
    
    fieldsets = (
        ('Invoice Information', {
            'fields': ('invoice_id', 'status', 'created_at', 'updated_at')
        }),
        ('Business Information', {
            'fields': ('business_name', 'business_email', 'business_address', 'business_phone')
        }),
        ('Client Information', {
            'fields': ('client_name', 'client_email', 'client_phone', 'client_address')
        }),
        ('Invoice Details', {
            'fields': ('description', 'quantity', 'unit_price', 'subtotal')
        }),
        ('Financial Details', {
            'fields': ('tax_rate', 'tax_amount', 'discount_amount', 'total_amount', 'currency')
        }),
        ('Payment Terms', {
            'fields': ('payment_terms', 'issue_date', 'due_date', 'paid_date', 'payment_instructions')
        }),
        ('Additional Information', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )
    
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('issue_date',)
        return self.readonly_fields
