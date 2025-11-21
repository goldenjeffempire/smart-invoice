from django.contrib import admin
from .models import Invoice, LineItem


class LineItemInline(admin.TabularInline):
    model = LineItem
    extra = 1


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("invoice_id", "client_name", "business_name", "status", "total", "created_at")
    list_filter = ("status", "currency", "created_at")
    search_fields = ("invoice_id", "client_name", "business_name", "client_email")
    readonly_fields = ("invoice_id", "created_at", "updated_at")
    inlines = [LineItemInline]

    fieldsets = (
        (
            "Invoice Information",
            {"fields": ("invoice_id", "user", "status", "currency", "tax_rate")},
        ),
        (
            "Business Details",
            {"fields": ("business_name", "business_email", "business_phone", "business_address")},
        ),
        (
            "Client Details",
            {"fields": ("client_name", "client_email", "client_phone", "client_address")},
        ),
        ("Dates", {"fields": ("invoice_date", "due_date")}),
        ("Branding", {"fields": ("brand_name", "brand_color", "logo")}),
        ("Bank Details", {"fields": ("bank_name", "account_name", "account_number")}),
        ("Additional", {"fields": ("notes", "created_at", "updated_at")}),
    )


@admin.register(LineItem)
class LineItemAdmin(admin.ModelAdmin):
    list_display = ("invoice", "description", "quantity", "unit_price", "total")
    search_fields = ("description", "invoice__invoice_id")
