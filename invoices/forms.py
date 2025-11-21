from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Invoice, LineItem
from .validators import (
    validate_phone_number,
    validate_tax_rate,
    validate_invoice_date,
    validate_bank_account,
    validate_hex_color,
    validate_email_domain,
    validate_positive_decimal,
    InvoiceBusinessRules,
)


class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        validators=[validate_email_domain],
        widget=forms.EmailInput(attrs={
            'class': 'input-field',
            'placeholder': 'your.email@example.com',
            'autocomplete': 'email',
        })
    )
    first_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'input-field',
            'placeholder': 'First Name',
            'autocomplete': 'given-name',
        })
    )
    last_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'input-field',
            'placeholder': 'Last Name',
            'autocomplete': 'family-name',
        })
    )

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password1", "password2")
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'input-field',
                'placeholder': 'Username',
                'autocomplete': 'username',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'input-field',
            'placeholder': 'Password',
            'autocomplete': 'new-password',
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'input-field',
            'placeholder': 'Confirm Password',
            'autocomplete': 'new-password',
        })


class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = [
            "business_name",
            "business_email",
            "business_phone",
            "business_address",
            "client_name",
            "client_email",
            "client_phone",
            "client_address",
            "invoice_date",
            "due_date",
            "currency",
            "tax_rate",
            "brand_name",
            "brand_color",
            "logo",
            "bank_name",
            "account_name",
            "account_number",
            "notes",
            "status",
        ]
        widgets = {
            "business_name": forms.TextInput(attrs={
                "class": "input-field",
                "placeholder": "Your Business Name",
            }),
            "business_email": forms.EmailInput(attrs={
                "class": "input-field",
                "placeholder": "business@example.com",
            }),
            "business_phone": forms.TextInput(attrs={
                "class": "input-field",
                "placeholder": "+1 (555) 123-4567",
            }),
            "business_address": forms.Textarea(attrs={
                "rows": 3,
                "class": "input-field",
                "placeholder": "123 Business St, City, State ZIP",
            }),
            "client_name": forms.TextInput(attrs={
                "class": "input-field",
                "placeholder": "Client Name",
            }),
            "client_email": forms.EmailInput(attrs={
                "class": "input-field",
                "placeholder": "client@example.com",
            }),
            "client_phone": forms.TextInput(attrs={
                "class": "input-field",
                "placeholder": "+1 (555) 987-6543",
            }),
            "client_address": forms.Textarea(attrs={
                "rows": 3,
                "class": "input-field",
                "placeholder": "456 Client Ave, City, State ZIP",
            }),
            "notes": forms.Textarea(attrs={
                "rows": 3,
                "class": "input-field",
                "placeholder": "Additional notes or payment terms...",
            }),
            "invoice_date": forms.DateInput(attrs={
                "type": "date",
                "class": "input-field",
            }),
            "due_date": forms.DateInput(attrs={
                "type": "date",
                "class": "input-field",
            }),
            "brand_color": forms.TextInput(attrs={
                "type": "color",
                "class": "h-12 w-full cursor-pointer",
            }),
            "brand_name": forms.TextInput(attrs={
                "class": "input-field",
                "placeholder": "Your Brand",
            }),
            "bank_name": forms.TextInput(attrs={
                "class": "input-field",
                "placeholder": "Bank Name",
            }),
            "account_name": forms.TextInput(attrs={
                "class": "input-field",
                "placeholder": "Account Holder Name",
            }),
            "account_number": forms.TextInput(attrs={
                "class": "input-field",
                "placeholder": "Account Number",
            }),
            "currency": forms.Select(attrs={
                "class": "input-field",
            }),
            "tax_rate": forms.NumberInput(attrs={
                "class": "input-field",
                "placeholder": "0.00",
                "step": "0.01",
                "min": "0",
                "max": "100",
            }),
            "status": forms.Select(attrs={
                "class": "input-field",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add custom validators
        self.fields['business_phone'].validators.append(validate_phone_number)
        self.fields['client_phone'].validators.append(validate_phone_number)
        self.fields['business_email'].validators.append(validate_email_domain)
        self.fields['client_email'].validators.append(validate_email_domain)
        self.fields['tax_rate'].validators.append(validate_tax_rate)
        self.fields['invoice_date'].validators.append(validate_invoice_date)
        self.fields['brand_color'].validators.append(validate_hex_color)
        self.fields['account_number'].validators.append(validate_bank_account)
        
        # Mark required fields
        for field_name, field in self.fields.items():
            if field.required:
                field.label_suffix = " *"

    def clean(self):
        cleaned_data = super().clean()
        invoice_date = cleaned_data.get("invoice_date")
        due_date = cleaned_data.get("due_date")
        
        # Validate due date is after invoice date
        if invoice_date and due_date:
            InvoiceBusinessRules.validate_due_date(invoice_date, due_date)
        
        return cleaned_data


class LineItemForm(forms.ModelForm):
    class Meta:
        model = LineItem
        fields = ["description", "quantity", "unit_price"]
        widgets = {
            "description": forms.TextInput(attrs={
                "class": "input-field",
                "placeholder": "Item description",
            }),
            "quantity": forms.NumberInput(attrs={
                "class": "input-field",
                "step": "0.01",
                "min": "0.01",
                "placeholder": "1.00",
            }),
            "unit_price": forms.NumberInput(attrs={
                "class": "input-field",
                "step": "0.01",
                "min": "0",
                "placeholder": "0.00",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['quantity'].validators.append(validate_positive_decimal)
        self.fields['unit_price'].validators.append(validate_positive_decimal)
