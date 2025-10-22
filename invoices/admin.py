# invoices/admin.py
from django.contrib import admin
from .models import Invoice, Client, PaymentTransaction, InvoiceLineItem, SupportInquiry


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'company_name', 'total_invoices', 'total_revenue', 'created_at')
    list_filter = ('created_at', 'user')
    search_fields = ('name', 'email', 'phone', 'company_name', 'tax_id')
    readonly_fields = ('created_at', 'updated_at', 'total_invoices', 'total_revenue')
    
    fieldsets = (
        ('Client Information', {
            'fields': ('user', 'name', 'email', 'phone', 'company_name', 'tax_id')
        }),
        ('Address', {
            'fields': ('address',)
        }),
        ('Additional', {
            'fields': ('notes', 'created_at', 'updated_at', 'total_invoices', 'total_revenue')
        }),
    )
    
    date_hierarchy = 'created_at'
    ordering = ('name',)


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_reference', 'invoice', 'amount', 'currency', 'status', 'payment_method', 'payment_date', 'created_at')
    list_filter = ('status', 'payment_method', 'currency', 'created_at')
    search_fields = ('transaction_reference', 'invoice__invoice_id', 'paid_by', 'payment_email')
    readonly_fields = ('created_at', 'updated_at', 'paystack_response')
    
    fieldsets = (
        ('Transaction Information', {
            'fields': ('invoice', 'transaction_reference', 'payment_method', 'status')
        }),
        ('Amount Details', {
            'fields': ('amount', 'currency', 'payment_date')
        }),
        ('Payer Information', {
            'fields': ('paid_by', 'payment_email', 'payment_phone')
        }),
        ('Additional Details', {
            'fields': ('paystack_response', 'notes', 'created_at', 'updated_at')
        }),
    )
    
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)


class InvoiceLineItemInline(admin.TabularInline):
    model = InvoiceLineItem
    extra = 1
    fields = ('description', 'quantity', 'unit_price', 'amount', 'order')
    readonly_fields = ('amount',)


@admin.register(SupportInquiry)
class SupportInquiryAdmin(admin.ModelAdmin):
    list_display = ('subject', 'name', 'email', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Inquiry Information', {
            'fields': ('name', 'email', 'subject', 'is_read')
        }),
        ('Message', {
            'fields': ('message',)
        }),
        ('Metadata', {
            'fields': ('created_at',)
        }),
    )
    
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    
    actions = ['mark_as_read', 'mark_as_unread']
    
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
    mark_as_read.short_description = "Mark selected inquiries as read"
    
    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)
    mark_as_unread.short_description = "Mark selected inquiries as unread"


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
