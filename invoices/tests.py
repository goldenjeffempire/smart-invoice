from django.test import TestCase, Client
from django.contrib.auth.models import User
from decimal import Decimal
from .models import Invoice, LineItem


class InvoiceModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )

    def test_create_invoice(self):
        invoice = Invoice.objects.create(
            user=self.user,
            business_name="Test Business",
            business_email="business@test.com",
            business_phone="+1234567890",
            business_address="123 Test St",
            client_name="Test Client",
            client_email="client@test.com",
            client_phone="+9876543210",
            client_address="456 Client Ave",
            currency="USD",
            tax_rate=Decimal("10"),
        )
        self.assertTrue(invoice.invoice_id)
        self.assertEqual(invoice.status, "unpaid")
        self.assertIsNotNone(invoice.created_at)

    def test_invoice_total_calculation(self):
        invoice = Invoice.objects.create(
            user=self.user,
            business_name="Test Business",
            business_email="business@test.com",
            business_phone="+1234567890",
            business_address="123 Test St",
            client_name="Test Client",
            client_email="client@test.com",
            client_phone="+9876543210",
            client_address="456 Client Ave",
            currency="USD",
            tax_rate=Decimal("10"),
        )
        LineItem.objects.create(
            invoice=invoice,
            description="Test Item",
            quantity=Decimal("2"),
            unit_price=Decimal("100"),
        )
        # Subtotal: 200, Tax: 20, Total: 220
        self.assertEqual(invoice.subtotal, Decimal("200"))
        self.assertEqual(invoice.tax_amount, Decimal("20"))
        self.assertEqual(invoice.total, Decimal("220"))

    def test_invoice_properties(self):
        invoice = Invoice.objects.create(
            user=self.user,
            business_name="Test Business",
            business_email="business@test.com",
            business_phone="+1234567890",
            business_address="123 Test St",
            client_name="Test Client",
            client_email="client@test.com",
            client_phone="+9876543210",
            client_address="456 Client Ave",
            currency="USD",
            tax_rate=Decimal("5"),
        )
        self.assertIsNotNone(invoice.invoice_id)
        self.assertEqual(invoice.get_status_display(), "Unpaid")


class AuthenticationTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )

    def test_signup_page_loads(self):
        response = self.client.get("/signup/")
        self.assertEqual(response.status_code, 200)

    def test_login_page_loads(self):
        response = self.client.get("/login/")
        self.assertEqual(response.status_code, 200)

    def test_login_successful(self):
        response = self.client.post(
            "/login/",
            {"username": "testuser", "password": "testpass123"},
            follow=True,
        )
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_home_page_loads(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_features_page_loads(self):
        response = self.client.get("/features/")
        self.assertEqual(response.status_code, 200)


class InvoiceViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        self.invoice = Invoice.objects.create(
            user=self.user,
            business_name="Test Business",
            business_email="business@test.com",
            business_phone="+1234567890",
            business_address="123 Test St",
            client_name="Test Client",
            client_email="client@test.com",
            client_phone="+9876543210",
            client_address="456 Client Ave",
            currency="USD",
            tax_rate=Decimal("10"),
        )

    def test_dashboard_requires_login(self):
        response = self.client.get("/invoices/dashboard/", follow=True)
        self.assertRedirects(response, "/login/?next=/invoices/dashboard/")

    def test_dashboard_loads_for_authenticated_user(self):
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get("/invoices/dashboard/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("invoices", response.context)

    def test_invoice_detail_requires_ownership(self):
        other_user = User.objects.create_user(
            username="otheruser",
            email="other@example.com",
            password="otherpass123",
        )
        self.client.login(username=other_user.username, password="otherpass123")
        response = self.client.get(f"/invoices/invoice/{self.invoice.id}/")
        self.assertEqual(response.status_code, 404)

    def test_invoice_detail_loads_for_owner(self):
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(f"/invoices/invoice/{self.invoice.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["invoice"], self.invoice)


class PDFGenerationTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        self.invoice = Invoice.objects.create(
            user=self.user,
            business_name="Test Business",
            business_email="business@test.com",
            business_phone="+1234567890",
            business_address="123 Test St",
            client_name="Test Client",
            client_email="client@test.com",
            client_phone="+9876543210",
            client_address="456 Client Ave",
            currency="USD",
            tax_rate=Decimal("10"),
        )

    def test_pdf_generation_endpoint_exists(self):
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(f"/invoices/invoice/{self.invoice.id}/pdf/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")


class MultiCurrencyTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )

    def test_invoice_supports_multiple_currencies(self):
        currencies = ["USD", "EUR", "GBP", "NGN", "CAD", "AUD"]
        for currency in currencies:
            invoice = Invoice.objects.create(
                user=self.user,
                business_name="Test Business",
                business_email="business@test.com",
                business_phone="+1234567890",
                business_address="123 Test St",
                client_name="Test Client",
                client_email="client@test.com",
                client_phone="+9876543210",
                client_address="456 Client Ave",
                currency=currency,
                tax_rate=Decimal("10"),
            )
            self.assertEqual(invoice.currency, currency)
