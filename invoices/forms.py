# invoices/forms.py
from django import forms
from .models import Invoice, SupportInquiry, Client, UserSettings
from datetime import timedelta
from django.utils import timezone

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = [
            'business_name', 'business_email', 'business_address', 'business_phone',
            'client_name', 'client_email', 'client_phone', 'client_address',
            'description', 'quantity', 'unit_price', 
            'tax_rate', 'discount_amount', 'currency',
            'status', 'payment_terms', 'issue_date', 'due_date',
            'notes', 'payment_instructions'
        ]
        widgets = {
            'business_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Company Name'
            }),
            'business_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'company@example.com'
            }),
            'business_address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': '123 Business St, City, Country'
            }),
            'business_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+1 (555) 123-4567'
            }),
            'client_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Client Company Name'
            }),
            'client_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'client@example.com'
            }),
            'client_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+1 (555) 987-6543 or WhatsApp number'
            }),
            'client_address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': '456 Client Ave, City, Country'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe the product or service provided...'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01'
            }),
            'unit_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01'
            }),
            'tax_rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'discount_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'currency': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'payment_terms': forms.Select(attrs={'class': 'form-control'}),
            'issue_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'due_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Any additional notes for the client...'
            }),
            'payment_instructions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Bank details, payment methods, etc...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields['issue_date'].initial = timezone.now().date()
            self.fields['due_date'].initial = timezone.now().date() + timedelta(days=30)


class SupportInquiryForm(forms.ModelForm):
    class Meta:
        model = SupportInquiry
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-purple-200 focus:border-purple-500 focus:ring-2 focus:ring-purple-200 transition',
                'placeholder': 'Your Full Name',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-purple-200 focus:border-purple-500 focus:ring-2 focus:ring-purple-200 transition',
                'placeholder': 'your.email@example.com',
                'required': True
            }),
            'subject': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-purple-200 focus:border-purple-500 focus:ring-2 focus:ring-purple-200 transition',
                'placeholder': 'How can we help you?',
                'required': True
            }),
            'message': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-purple-200 focus:border-purple-500 focus:ring-2 focus:ring-purple-200 transition',
                'placeholder': 'Please describe your inquiry in detail...',
                'rows': 6,
                'required': True
            }),
        }


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = [
            'name', 'email', 'phone', 'address', 
            'company_name', 'tax_id', 'notes'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Client Full Name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': 'client@example.com'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': '+1 (555) 123-4567'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 3,
                'placeholder': '123 Client St, City, Country'
            }),
            'company_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Company Name (Optional)'
            }),
            'tax_id': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Tax ID / VAT Number (Optional)'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 3,
                'placeholder': 'Additional notes about this client...'
            }),
        }


class BusinessInfoForm(forms.ModelForm):
    class Meta:
        model = UserSettings
        fields = [
            'business_name', 'business_email', 'business_phone', 
            'business_address', 'business_website', 'business_tax_id', 'business_logo'
        ]
        widgets = {
            'business_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Your Business Name'
            }),
            'business_email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': 'business@example.com'
            }),
            'business_phone': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': '+1 (555) 123-4567'
            }),
            'business_address': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 3,
                'placeholder': '123 Business St, City, State, ZIP'
            }),
            'business_website': forms.URLInput(attrs={
                'class': 'form-input',
                'placeholder': 'https://yourwebsite.com'
            }),
            'business_tax_id': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Tax ID / EIN Number'
            }),
            'business_logo': forms.FileInput(attrs={
                'class': 'form-input',
                'accept': 'image/*'
            }),
        }


class AppearanceSettingsForm(forms.ModelForm):
    class Meta:
        model = UserSettings
        fields = ['theme', 'custom_primary_color', 'custom_secondary_color']
        widgets = {
            'theme': forms.Select(attrs={'class': 'form-input'}),
            'custom_primary_color': forms.TextInput(attrs={
                'class': 'form-input',
                'type': 'color',
                'placeholder': '#8b5cf6'
            }),
            'custom_secondary_color': forms.TextInput(attrs={
                'class': 'form-input',
                'type': 'color',
                'placeholder': '#ec4899'
            }),
        }


class PaymentSettingsForm(forms.ModelForm):
    class Meta:
        model = UserSettings
        fields = [
            'enable_paystack', 'paystack_public_key', 
            'paystack_secret_key', 'paystack_webhook_secret'
        ]
        widgets = {
            'enable_paystack': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'paystack_public_key': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'pk_test_...'
            }),
            'paystack_secret_key': forms.PasswordInput(attrs={
                'class': 'form-input',
                'placeholder': 'sk_test_...'
            }),
            'paystack_webhook_secret': forms.PasswordInput(attrs={
                'class': 'form-input',
                'placeholder': 'whsec_...'
            }),
        }


class EmailSettingsForm(forms.ModelForm):
    class Meta:
        model = UserSettings
        fields = [
            'email_provider', 'email_host', 'email_port', 'email_username',
            'email_password', 'email_use_tls', 'sendgrid_api_key'
        ]
        widgets = {
            'email_provider': forms.Select(attrs={'class': 'form-input'}),
            'email_host': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'smtp.gmail.com'
            }),
            'email_port': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': '587'
            }),
            'email_username': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': 'your-email@gmail.com'
            }),
            'email_password': forms.PasswordInput(attrs={
                'class': 'form-input',
                'placeholder': 'App Password or SMTP Password'
            }),
            'email_use_tls': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'sendgrid_api_key': forms.PasswordInput(attrs={
                'class': 'form-input',
                'placeholder': 'SG.xxxxxxxxxxxxxxx'
            }),
        }


class WhatsAppSettingsForm(forms.ModelForm):
    class Meta:
        model = UserSettings
        fields = [
            'enable_whatsapp_notifications', 'twilio_account_sid',
            'twilio_auth_token', 'twilio_whatsapp_number', 'whatsapp_number'
        ]
        widgets = {
            'enable_whatsapp_notifications': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'twilio_account_sid': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'ACxxxxxxxxxxxxxxx'
            }),
            'twilio_auth_token': forms.PasswordInput(attrs={
                'class': 'form-input',
                'placeholder': 'Auth Token'
            }),
            'twilio_whatsapp_number': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'whatsapp:+14155238886'
            }),
            'whatsapp_number': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': '+1234567890'
            }),
        }


class InvoiceDefaultsForm(forms.ModelForm):
    class Meta:
        model = UserSettings
        fields = [
            'default_currency', 'default_payment_terms', 'default_tax_rate',
            'invoice_footer_text'
        ]
        widgets = {
            'default_currency': forms.Select(attrs={'class': 'form-input'}),
            'default_payment_terms': forms.Select(attrs={'class': 'form-input'}),
            'default_tax_rate': forms.NumberInput(attrs={
                'class': 'form-input',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'invoice_footer_text': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 3,
                'placeholder': 'Thank you for your business!'
            }),
        }


class NotificationSettingsForm(forms.ModelForm):
    class Meta:
        model = UserSettings
        fields = [
            'enable_email_notifications', 'enable_sms_notifications',
            'enable_payment_reminders', 'reminder_days_before_due',
            'reminder_days_after_overdue'
        ]
        widgets = {
            'enable_email_notifications': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'enable_sms_notifications': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'enable_payment_reminders': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'reminder_days_before_due': forms.NumberInput(attrs={
                'class': 'form-input',
                'min': '1',
                'placeholder': '3'
            }),
            'reminder_days_after_overdue': forms.NumberInput(attrs={
                'class': 'form-input',
                'min': '1',
                'placeholder': '3'
            }),
        }
