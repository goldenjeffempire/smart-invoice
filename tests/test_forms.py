import pytest
from decimal import Decimal
from django.contrib.auth.models import User
from invoices.forms import SignUpForm, InvoiceForm, LineItemForm
from invoices.models import Invoice, LineItem


@pytest.mark.django_db
class TestSignUpForm:
    def test_signup_form_valid_data(self):
        form = SignUpForm(
            data={
                "username": "newuser",
                "first_name": "New",
                "last_name": "User",
                "email": "newuser@test.com",
                "password1": "ComplexPass123!",
                "password2": "ComplexPass123!",
            }
        )
        assert form.is_valid()

    def test_signup_form_passwords_must_match(self):
        form = SignUpForm(
            data={
                "username": "newuser",
                "first_name": "New",
                "last_name": "User",
                "email": "newuser@test.com",
                "password1": "ComplexPass123!",
                "password2": "DifferentPass123!",
            }
        )
        assert not form.is_valid()
        assert "password2" in form.errors

    def test_signup_form_requires_email(self):
        form = SignUpForm(
            data={
                "username": "newuser",
                "first_name": "New",
                "last_name": "User",
                "password1": "ComplexPass123!",
                "password2": "ComplexPass123!",
            }
        )
        assert not form.is_valid()
        assert "email" in form.errors

    def test_signup_form_requires_first_name(self):
        form = SignUpForm(
            data={
                "username": "newuser",
                "last_name": "User",
                "email": "newuser@test.com",
                "password1": "ComplexPass123!",
                "password2": "ComplexPass123!",
            }
        )
        assert not form.is_valid()
        assert "first_name" in form.errors

    def test_signup_form_requires_last_name(self):
        form = SignUpForm(
            data={
                "username": "newuser",
                "first_name": "New",
                "email": "newuser@test.com",
                "password1": "ComplexPass123!",
                "password2": "ComplexPass123!",
            }
        )
        assert not form.is_valid()
        assert "last_name" in form.errors

    def test_signup_form_creates_user_on_save(self):
        form = SignUpForm(
            data={
                "username": "newuser",
                "first_name": "New",
                "last_name": "User",
                "email": "newuser@test.com",
                "password1": "ComplexPass123!",
                "password2": "ComplexPass123!",
            }
        )
        assert form.is_valid()
        user = form.save()
        assert User.objects.filter(username="newuser").exists()
        assert user.email == "newuser@test.com"
        assert user.first_name == "New"
        assert user.last_name == "User"


@pytest.mark.django_db
class TestInvoiceForm:
    def test_invoice_form_valid_data(self):
        form = InvoiceForm(
            data={
                "business_name": "Test Business",
                "business_email": "business@test.com",
                "business_phone": "+1234567890",
                "business_address": "123 Business St",
                "client_name": "Test Client",
                "client_email": "client@test.com",
                "client_phone": "+0987654321",
                "client_address": "456 Client Ave",
                "invoice_date": "2024-01-01",
                "due_date": "2024-01-31",
                "currency": "USD",
                "tax_rate": Decimal("10.00"),
                "brand_name": "Test Brand",
                "brand_color": "#6366f1",
                "bank_name": "Test Bank",
                "account_name": "Test Account",
                "account_number": "123456789",
                "notes": "Test notes",
                "status": "unpaid",
            }
        )
        assert form.is_valid()

    def test_invoice_form_requires_business_name(self):
        form = InvoiceForm(
            data={
                "business_email": "business@test.com",
                "business_address": "123 Business St",
                "client_name": "Test Client",
                "client_email": "client@test.com",
                "client_address": "456 Client Ave",
                "invoice_date": "2024-01-01",
                "due_date": "2024-01-31",
                "currency": "USD",
            }
        )
        assert not form.is_valid()
        assert "business_name" in form.errors

    def test_invoice_form_requires_business_email(self):
        form = InvoiceForm(
            data={
                "business_name": "Test Business",
                "business_address": "123 Business St",
                "client_name": "Test Client",
                "client_email": "client@test.com",
                "client_address": "456 Client Ave",
                "invoice_date": "2024-01-01",
                "due_date": "2024-01-31",
                "currency": "USD",
            }
        )
        assert not form.is_valid()
        assert "business_email" in form.errors

    def test_invoice_form_requires_valid_email_format(self):
        form = InvoiceForm(
            data={
                "business_name": "Test Business",
                "business_email": "invalid-email",
                "business_address": "123 Business St",
                "client_name": "Test Client",
                "client_email": "client@test.com",
                "client_address": "456 Client Ave",
                "invoice_date": "2024-01-01",
                "due_date": "2024-01-31",
                "currency": "USD",
            }
        )
        assert not form.is_valid()
        assert "business_email" in form.errors

    def test_invoice_form_currency_choices(self):
        valid_currencies = ["USD", "EUR", "GBP", "NGN", "CAD", "AUD"]
        for currency in valid_currencies:
            form = InvoiceForm(
                data={
                    "business_name": "Test Business",
                    "business_email": "business@test.com",
                    "business_phone": "+1234567890",
                    "business_address": "123 Business St",
                    "client_name": "Test Client",
                    "client_email": "client@test.com",
                    "client_phone": "+0987654321",
                    "client_address": "456 Client Ave",
                    "invoice_date": "2024-01-01",
                    "due_date": "2024-01-31",
                    "currency": currency,
                    "tax_rate": Decimal("0.00"),
                    "status": "unpaid",
                }
            )
            assert form.is_valid(), f"Currency {currency} should be valid but got errors: {form.errors}"

    def test_invoice_form_invalid_currency(self):
        form = InvoiceForm(
            data={
                "business_name": "Test Business",
                "business_email": "business@test.com",
                "business_address": "123 Business St",
                "client_name": "Test Client",
                "client_email": "client@test.com",
                "client_address": "456 Client Ave",
                "invoice_date": "2024-01-01",
                "due_date": "2024-01-31",
                "currency": "INVALID",
            }
        )
        assert not form.is_valid()
        assert "currency" in form.errors

    def test_invoice_form_date_widget_type(self):
        form = InvoiceForm()
        assert form.fields["invoice_date"].widget.input_type == "date"
        assert form.fields["due_date"].widget.input_type == "date"

    def test_invoice_form_color_widget_type(self):
        form = InvoiceForm()
        assert form.fields["brand_color"].widget.input_type == "color"


@pytest.mark.django_db
class TestLineItemForm:
    def test_line_item_form_valid_data(self):
        form = LineItemForm(
            data={
                "description": "Test Service",
                "quantity": Decimal("5.00"),
                "unit_price": Decimal("100.00"),
            }
        )
        assert form.is_valid()

    def test_line_item_form_requires_description(self):
        form = LineItemForm(
            data={
                "quantity": Decimal("5.00"),
                "unit_price": Decimal("100.00"),
            }
        )
        assert not form.is_valid()
        assert "description" in form.errors

    def test_line_item_form_requires_quantity(self):
        form = LineItemForm(
            data={
                "description": "Test Service",
                "unit_price": Decimal("100.00"),
            }
        )
        assert not form.is_valid()
        assert "quantity" in form.errors

    def test_line_item_form_requires_unit_price(self):
        form = LineItemForm(
            data={
                "description": "Test Service",
                "quantity": Decimal("5.00"),
            }
        )
        assert not form.is_valid()
        assert "unit_price" in form.errors

    def test_line_item_form_quantity_must_be_decimal(self):
        form = LineItemForm(
            data={
                "description": "Test Service",
                "quantity": "not-a-number",
                "unit_price": Decimal("100.00"),
            }
        )
        assert not form.is_valid()
        assert "quantity" in form.errors

    def test_line_item_form_unit_price_must_be_decimal(self):
        form = LineItemForm(
            data={
                "description": "Test Service",
                "quantity": Decimal("5.00"),
                "unit_price": "not-a-number",
            }
        )
        assert not form.is_valid()
        assert "unit_price" in form.errors

    def test_line_item_form_creates_valid_instance(self, sample_invoice):
        form = LineItemForm(
            data={
                "description": "Test Service",
                "quantity": Decimal("3.00"),
                "unit_price": Decimal("150.00"),
            }
        )
        assert form.is_valid()
        line_item = form.save(commit=False)
        line_item.invoice = sample_invoice
        line_item.save()
        assert LineItem.objects.filter(description="Test Service").exists()
        assert line_item.total == Decimal("450.00")
