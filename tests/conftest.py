import pytest
from django.contrib.auth.models import User
from invoices.models import Invoice, LineItem
from decimal import Decimal


@pytest.fixture
def user(db):
    """Create a test user"""
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123",
        first_name="Test",
        last_name="User",
    )


@pytest.fixture
def authenticated_client(client, user):
    """Create an authenticated client"""
    client.login(username="testuser", password="testpass123")
    return client


@pytest.fixture
def sample_invoice(user):
    """Create a sample invoice for testing"""
    invoice = Invoice.objects.create(
        user=user,
        business_name="Test Business Inc",
        business_email="business@test.com",
        business_phone="+1234567890",
        business_address="123 Business St, City, Country",
        client_name="Test Client",
        client_email="client@test.com",
        client_phone="+0987654321",
        client_address="456 Client Ave, City, Country",
        currency="USD",
        tax_rate=Decimal("10.00"),
        brand_name="Test Brand",
        brand_color="#6366f1",
        bank_name="Test Bank",
        account_name="Test Account",
        account_number="1234567890",
        notes="Test notes",
        status="unpaid",
    )
    return invoice


@pytest.fixture
def sample_invoice_with_items(sample_invoice):
    """Create a sample invoice with line items"""
    LineItem.objects.create(
        invoice=sample_invoice,
        description="Web Development",
        quantity=Decimal("10.00"),
        unit_price=Decimal("100.00"),
    )
    LineItem.objects.create(
        invoice=sample_invoice,
        description="Design Work",
        quantity=Decimal("5.00"),
        unit_price=Decimal("80.00"),
    )
    return sample_invoice
