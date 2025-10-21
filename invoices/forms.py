# invoices/forms.py
from django import forms
from .models import Invoice

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['business_name','client_name','client_email_or_whatsapp','description','amount','currency','notes']
        widgets = {
            'description': forms.Textarea(attrs={'rows':3}),
            'notes': forms.Textarea(attrs={'rows':2}),
        }
