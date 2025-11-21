import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from invoices.models import Invoice
import json


@pytest.mark.django_db
class TestAuthenticationViews:
    def test_home_view(self, client):
        """Test home page loads successfully"""
        response = client.get(reverse("home"))
        assert response.status_code == 200

    def test_signup_view_get(self, client):
        """Test signup page loads"""
        response = client.get(reverse("signup"))
        assert response.status_code == 200

    def test_signup_view_post_success(self, client):
        """Test user can sign up successfully"""
        data = {
            "username": "newuser",
            "email": "newuser@test.com",
            "first_name": "New",
            "last_name": "User",
            "password1": "ComplexPass123!",
            "password2": "ComplexPass123!",
        }
        response = client.post(reverse("signup"), data)
        assert response.status_code == 302  # Redirect after success
        assert User.objects.filter(username="newuser").exists()

    def test_login_view_get(self, client):
        """Test login page loads"""
        response = client.get(reverse("login"))
        assert response.status_code == 200

    def test_login_view_post_success(self, client, user):
        """Test user can log in successfully"""
        response = client.post(
            reverse("login"), {"username": "testuser", "password": "testpass123"}
        )
        assert response.status_code == 302  # Redirect after success

    def test_login_view_post_failure(self, client):
        """Test login fails with wrong credentials"""
        response = client.post(
            reverse("login"), {"username": "wronguser", "password": "wrongpass"}
        )
        assert response.status_code == 200
        assert b"Invalid username or password" in response.content

    def test_logout_view(self, authenticated_client):
        """Test user can log out"""
        response = authenticated_client.get(reverse("logout"))
        assert response.status_code == 302


@pytest.mark.django_db
class TestDashboardView:
    def test_dashboard_requires_login(self, client):
        """Test dashboard redirects if not logged in"""
        response = client.get(reverse("dashboard"))
        assert response.status_code == 302
        assert "/login/" in response.url

    def test_dashboard_loads_for_authenticated_user(self, authenticated_client):
        """Test dashboard loads for logged in user"""
        response = authenticated_client.get(reverse("dashboard"))
        assert response.status_code == 200

    def test_dashboard_displays_user_invoices(
        self, authenticated_client, sample_invoice_with_items
    ):
        """Test dashboard shows user's invoices"""
        response = authenticated_client.get(reverse("dashboard"))
        assert response.status_code == 200
        assert sample_invoice_with_items.invoice_id in response.content.decode()

    def test_dashboard_filter_paid(self, authenticated_client, user):
        """Test dashboard can filter paid invoices"""
        Invoice.objects.create(
            user=user,
            business_name="Business",
            business_email="b@test.com",
            business_address="Address",
            client_name="Client",
            client_email="c@test.com",
            client_address="Address",
            status="paid",
        )
        Invoice.objects.create(
            user=user,
            business_name="Business 2",
            business_email="b2@test.com",
            business_address="Address 2",
            client_name="Client 2",
            client_email="c2@test.com",
            client_address="Address 2",
            status="unpaid",
        )
        response = authenticated_client.get(reverse("dashboard") + "?status=paid")
        assert response.status_code == 200
        assert response.context["filter_status"] == "paid"


@pytest.mark.django_db
class TestInvoiceCRUDViews:
    def test_create_invoice_view_get(self, authenticated_client):
        """Test create invoice page loads"""
        response = authenticated_client.get(reverse("create_invoice"))
        assert response.status_code == 200

    def test_create_invoice_view_post_success(self, authenticated_client):
        """Test creating an invoice via POST"""
        data = {
            "business_name": "My Business",
            "business_email": "business@test.com",
            "business_phone": "+1234567890",
            "business_address": "123 Business St",
            "client_name": "Client Name",
            "client_email": "client@test.com",
            "client_phone": "+0987654321",
            "client_address": "456 Client Ave",
            "invoice_date": "2025-01-01",
            "due_date": "2025-01-31",
            "currency": "USD",
            "tax_rate": "10.00",
            "brand_name": "Brand",
            "brand_color": "#6366f1",
            "bank_name": "Bank",
            "account_name": "Account",
            "account_number": "123456",
            "notes": "Test notes",
            "status": "unpaid",
            "line_items": json.dumps(
                [
                    {
                        "description": "Service 1",
                        "quantity": "1.00",
                        "unit_price": "100.00",
                    },
                    {"description": "Service 2", "quantity": "2.00", "unit_price": "50.00"},
                ]
            ),
        }
        response = authenticated_client.post(reverse("create_invoice"), data)
        assert response.status_code == 302
        assert Invoice.objects.filter(client_name="Client Name").exists()
        invoice = Invoice.objects.get(client_name="Client Name")
        assert invoice.line_items.count() == 2

    def test_invoice_detail_view(self, authenticated_client, sample_invoice):
        """Test invoice detail page loads"""
        response = authenticated_client.get(
            reverse("invoice_detail", kwargs={"invoice_id": sample_invoice.id})
        )
        assert response.status_code == 200
        assert sample_invoice.client_name in response.content.decode()

    def test_edit_invoice_view_get(self, authenticated_client, sample_invoice_with_items):
        """Test edit invoice page loads with existing data"""
        response = authenticated_client.get(
            reverse("edit_invoice", kwargs={"invoice_id": sample_invoice_with_items.id})
        )
        assert response.status_code == 200
        assert sample_invoice_with_items.client_name in response.content.decode()

    def test_delete_invoice_view(
        self, authenticated_client, sample_invoice
    ):
        """Test deleting an invoice"""
        invoice_id = sample_invoice.id
        response = authenticated_client.post(
            reverse("delete_invoice", kwargs={"invoice_id": invoice_id})
        )
        assert response.status_code == 302
        assert not Invoice.objects.filter(id=invoice_id).exists()

    def test_update_invoice_status(self, authenticated_client, sample_invoice):
        """Test updating invoice status"""
        assert sample_invoice.status == "unpaid"
        response = authenticated_client.post(
            reverse("update_invoice_status", kwargs={"invoice_id": sample_invoice.id}),
            {"status": "paid"},
        )
        sample_invoice.refresh_from_db()
        assert sample_invoice.status == "paid"
        assert response.status_code == 302


@pytest.mark.django_db
class TestPDFGenerationView:
    def test_generate_pdf(self, authenticated_client, sample_invoice_with_items):
        """Test PDF generation"""
        response = authenticated_client.get(
            reverse("generate_pdf", kwargs={"invoice_id": sample_invoice_with_items.id})
        )
        assert response.status_code == 200
        assert response["Content-Type"] == "application/pdf"
        assert "Invoice_" in response["Content-Disposition"]


@pytest.mark.django_db
class TestEmailInvoiceView:
    def test_send_invoice_email_view_get(self, authenticated_client, sample_invoice):
        """Test send email page loads"""
        response = authenticated_client.get(
            reverse("send_invoice_email", kwargs={"invoice_id": sample_invoice.id})
        )
        assert response.status_code == 200


@pytest.mark.django_db
class TestWhatsAppShareView:
    def test_whatsapp_share_view(self, authenticated_client, sample_invoice):
        """Test WhatsApp share page loads and generates URL"""
        response = authenticated_client.get(
            reverse("whatsapp_share", kwargs={"invoice_id": sample_invoice.id})
        )
        assert response.status_code == 200
        assert b"wa.me" in response.content


@pytest.mark.django_db
class TestAnalyticsView:
    def test_analytics_view_requires_login(self, client):
        """Test analytics redirects if not logged in"""
        response = client.get(reverse("analytics"))
        assert response.status_code == 302

    def test_analytics_view_loads(self, authenticated_client):
        """Test analytics page loads"""
        response = authenticated_client.get(reverse("analytics"))
        assert response.status_code == 200

    def test_analytics_displays_metrics(
        self, authenticated_client, sample_invoice_with_items
    ):
        """Test analytics displays correct metrics"""
        sample_invoice_with_items.status = "paid"
        sample_invoice_with_items.save()

        response = authenticated_client.get(reverse("analytics"))
        assert response.status_code == 200
        assert response.context["total_invoices"] == 1
        assert response.context["paid_invoices"] == 1


@pytest.mark.django_db
class TestStaticPagesViews:
    """Test static page views"""

    def test_features_page(self, client):
        response = client.get(reverse("features"))
        assert response.status_code == 200

    def test_pricing_page(self, client):
        response = client.get(reverse("pricing"))
        assert response.status_code == 200

    def test_about_page(self, client):
        response = client.get(reverse("about"))
        assert response.status_code == 200

    def test_contact_page(self, client):
        response = client.get(reverse("contact"))
        assert response.status_code == 200

    def test_faq_page(self, client):
        response = client.get(reverse("faq"))
        assert response.status_code == 200

    def test_support_page(self, client):
        response = client.get(reverse("support"))
        assert response.status_code == 200

    def test_terms_page(self, client):
        response = client.get(reverse("terms"))
        assert response.status_code == 200

    def test_privacy_page(self, client):
        response = client.get(reverse("privacy"))
        assert response.status_code == 200
