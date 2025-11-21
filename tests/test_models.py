import pytest
from decimal import Decimal
from invoices.models import Invoice, LineItem


@pytest.mark.django_db
class TestInvoiceModel:
    def test_invoice_creation(self, user):
        """Test creating an invoice"""
        invoice = Invoice.objects.create(
            user=user,
            business_name="Test Business",
            business_email="business@test.com",
            business_address="123 Business St",
            client_name="Test Client",
            client_email="client@test.com",
            client_address="456 Client Ave",
            currency="USD",
            tax_rate=Decimal("10.00"),
        )
        assert invoice.invoice_id is not None
        assert invoice.invoice_id.startswith("INV")
        assert len(invoice.invoice_id) == 9
        assert invoice.status == "unpaid"

    def test_invoice_id_uniqueness(self, user):
        """Test that invoice IDs are unique"""
        invoice1 = Invoice.objects.create(
            user=user,
            business_name="Business 1",
            business_email="b1@test.com",
            business_address="Address 1",
            client_name="Client 1",
            client_email="c1@test.com",
            client_address="Address 1",
        )
        invoice2 = Invoice.objects.create(
            user=user,
            business_name="Business 2",
            business_email="b2@test.com",
            business_address="Address 2",
            client_name="Client 2",
            client_email="c2@test.com",
            client_address="Address 2",
        )
        assert invoice1.invoice_id != invoice2.invoice_id

    def test_invoice_subtotal_calculation(self, sample_invoice):
        """Test invoice subtotal calculation"""
        LineItem.objects.create(
            invoice=sample_invoice,
            description="Item 1",
            quantity=Decimal("2.00"),
            unit_price=Decimal("50.00"),
        )
        LineItem.objects.create(
            invoice=sample_invoice,
            description="Item 2",
            quantity=Decimal("3.00"),
            unit_price=Decimal("30.00"),
        )
        assert sample_invoice.subtotal == Decimal("190.00")

    def test_invoice_tax_calculation(self, sample_invoice):
        """Test invoice tax amount calculation"""
        sample_invoice.tax_rate = Decimal("10.00")
        sample_invoice.save()

        LineItem.objects.create(
            invoice=sample_invoice,
            description="Item 1",
            quantity=Decimal("10.00"),
            unit_price=Decimal("100.00"),
        )
        assert sample_invoice.subtotal == Decimal("1000.00")
        assert sample_invoice.tax_amount == Decimal("100.00")

    def test_invoice_total_calculation(self, sample_invoice):
        """Test invoice total calculation with tax"""
        sample_invoice.tax_rate = Decimal("15.00")
        sample_invoice.save()

        LineItem.objects.create(
            invoice=sample_invoice,
            description="Item 1",
            quantity=Decimal("10.00"),
            unit_price=Decimal("100.00"),
        )
        assert sample_invoice.total == Decimal("1150.00")

    def test_invoice_string_representation(self, sample_invoice):
        """Test invoice __str__ method"""
        assert sample_invoice.client_name in str(sample_invoice)
        assert sample_invoice.invoice_id in str(sample_invoice)

    def test_invoice_ordering(self, user):
        """Test that invoices are ordered by created_at descending"""
        invoice1 = Invoice.objects.create(
            user=user,
            business_name="Business 1",
            business_email="b1@test.com",
            business_address="Address 1",
            client_name="Client 1",
            client_email="c1@test.com",
            client_address="Address 1",
        )
        invoice2 = Invoice.objects.create(
            user=user,
            business_name="Business 2",
            business_email="b2@test.com",
            business_address="Address 2",
            client_name="Client 2",
            client_email="c2@test.com",
            client_address="Address 2",
        )
        invoices = list(Invoice.objects.all())
        assert invoices[0].id == invoice2.id
        assert invoices[1].id == invoice1.id


@pytest.mark.django_db
class TestLineItemModel:
    def test_line_item_creation(self, sample_invoice):
        """Test creating a line item"""
        line_item = LineItem.objects.create(
            invoice=sample_invoice,
            description="Test Service",
            quantity=Decimal("5.00"),
            unit_price=Decimal("100.00"),
        )
        assert line_item.description == "Test Service"
        assert line_item.quantity == Decimal("5.00")
        assert line_item.unit_price == Decimal("100.00")

    def test_line_item_total_calculation(self, sample_invoice):
        """Test line item total property"""
        line_item = LineItem.objects.create(
            invoice=sample_invoice,
            description="Test Service",
            quantity=Decimal("7.50"),
            unit_price=Decimal("120.00"),
        )
        assert line_item.total == Decimal("900.00")

    def test_line_item_string_representation(self, sample_invoice):
        """Test line item __str__ method"""
        line_item = LineItem.objects.create(
            invoice=sample_invoice,
            description="Test Service",
            quantity=Decimal("1.00"),
            unit_price=Decimal("100.00"),
        )
        assert "Test Service" in str(line_item)
        assert sample_invoice.invoice_id in str(line_item)

    def test_line_item_cascade_delete(self, sample_invoice_with_items):
        """Test that line items are deleted when invoice is deleted"""
        invoice_id = sample_invoice_with_items.id
        item_count = LineItem.objects.filter(invoice=sample_invoice_with_items).count()
        assert item_count == 2

        sample_invoice_with_items.delete()
        assert LineItem.objects.filter(invoice_id=invoice_id).count() == 0
