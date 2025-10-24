from typing import Optional, Dict, Any, List
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from ..models import Invoice, InvoiceLineItem, Client
import logging

logger = logging.getLogger(__name__)


class InvoiceService:
    
    @staticmethod
    def create_invoice(user, data: Dict[str, Any]) -> Invoice:
        try:
            with transaction.atomic():
                client = data.get('client')
                if isinstance(client, int):
                    client = Client.objects.get(pk=client, user=user)
                
                invoice = Invoice.objects.create(
                    user=user,
                    client=client,
                    business_name=data.get('business_name', ''),
                    business_email=data.get('business_email', ''),
                    business_address=data.get('business_address', ''),
                    business_phone=data.get('business_phone', ''),
                    client_name=data.get('client_name', client.name if client else ''),
                    client_email=data.get('client_email', client.email if client else ''),
                    client_phone=data.get('client_phone', client.phone if client else ''),
                    client_address=data.get('client_address', client.address if client else ''),
                    currency=data.get('currency', 'USD'),
                    tax_rate=data.get('tax_rate', Decimal('0.00')),
                    discount_amount=data.get('discount_amount', Decimal('0.00')),
                    status=data.get('status', 'draft'),
                    payment_terms=data.get('payment_terms', 'net_30'),
                    issue_date=data.get('issue_date', timezone.now().date()),
                    due_date=data.get('due_date'),
                    notes=data.get('notes', ''),
                    payment_instructions=data.get('payment_instructions', ''),
                )
                
                line_items = data.get('line_items', [])
                for index, item in enumerate(line_items):
                    InvoiceLineItem.objects.create(
                        invoice=invoice,
                        description=item.get('description', ''),
                        quantity=item.get('quantity', 1),
                        unit_price=item.get('unit_price', Decimal('0.00')),
                        order=index
                    )
                
                invoice.calculate_totals()
                invoice.save()
                
                logger.info(f"Invoice {invoice.invoice_id} created successfully by user {user.username}")
                return invoice
                
        except Exception as e:
            logger.error(f"Error creating invoice: {str(e)}")
            raise ValidationError(f"Failed to create invoice: {str(e)}")
    
    @staticmethod
    def update_invoice(invoice: Invoice, data: Dict[str, Any]) -> Invoice:
        try:
            with transaction.atomic():
                for field, value in data.items():
                    if field not in ['line_items', 'id', 'invoice_id', 'created_at']:
                        setattr(invoice, field, value)
                
                if 'line_items' in data:
                    invoice.line_items.all().delete()
                    for index, item in enumerate(data['line_items']):
                        InvoiceLineItem.objects.create(
                            invoice=invoice,
                            description=item.get('description', ''),
                            quantity=item.get('quantity', 1),
                            unit_price=item.get('unit_price', Decimal('0.00')),
                            order=index
                        )
                
                invoice.calculate_totals()
                invoice.save()
                
                logger.info(f"Invoice {invoice.invoice_id} updated successfully")
                return invoice
                
        except Exception as e:
            logger.error(f"Error updating invoice {invoice.invoice_id}: {str(e)}")
            raise ValidationError(f"Failed to update invoice: {str(e)}")
    
    @staticmethod
    def update_status(invoice: Invoice, new_status: str) -> Invoice:
        valid_statuses = ['draft', 'sent', 'paid', 'overdue', 'cancelled']
        if new_status not in valid_statuses:
            raise ValidationError(f"Invalid status: {new_status}")
        
        old_status = invoice.status
        invoice.status = new_status
        
        if new_status == 'paid' and not invoice.paid_date:
            invoice.paid_date = timezone.now()
        
        invoice.save()
        logger.info(f"Invoice {invoice.invoice_id} status changed from {old_status} to {new_status}")
        return invoice
    
    @staticmethod
    def check_overdue_invoices(user) -> int:
        today = timezone.now().date()
        overdue_invoices = Invoice.objects.filter(
            user=user,
            status__in=['sent', 'draft'],
            due_date__lt=today
        )
        
        count = overdue_invoices.update(status='overdue')
        if count > 0:
            logger.info(f"Marked {count} invoices as overdue for user {user.username}")
        return count
    
    @staticmethod
    def get_invoice_stats(user) -> Dict[str, Any]:
        invoices = Invoice.objects.filter(user=user)
        
        return {
            'total': invoices.count(),
            'draft': invoices.filter(status='draft').count(),
            'sent': invoices.filter(status='sent').count(),
            'paid': invoices.filter(status='paid').count(),
            'overdue': invoices.filter(status='overdue').count(),
            'cancelled': invoices.filter(status='cancelled').count(),
            'total_revenue': invoices.filter(status='paid').aggregate(
                total=models.Sum('total_amount'))['total'] or Decimal('0.00'),
            'pending_revenue': invoices.filter(
                status__in=['sent', 'draft']).aggregate(
                total=models.Sum('total_amount'))['total'] or Decimal('0.00'),
        }
    
    @staticmethod
    def duplicate_invoice(invoice: Invoice) -> Invoice:
        try:
            with transaction.atomic():
                line_items = list(invoice.line_items.all())
                
                invoice.pk = None
                invoice.id = None
                invoice.invoice_id = None
                invoice.status = 'draft'
                invoice.paid_date = None
                invoice.paystack_reference = None
                invoice.issue_date = timezone.now().date()
                invoice.due_date = None
                invoice.created_at = timezone.now()
                invoice.save()
                
                for item in line_items:
                    item.pk = None
                    item.id = None
                    item.invoice = invoice
                    item.save()
                
                logger.info(f"Invoice duplicated: new ID {invoice.invoice_id}")
                return invoice
                
        except Exception as e:
            logger.error(f"Error duplicating invoice: {str(e)}")
            raise ValidationError(f"Failed to duplicate invoice: {str(e)}")


from django.db import models
