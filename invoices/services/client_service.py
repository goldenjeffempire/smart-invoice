from typing import Optional, Dict, Any
from django.db import transaction
from django.core.exceptions import ValidationError
from ..models import Client, Invoice
import logging

logger = logging.getLogger(__name__)


class ClientService:
    
    @staticmethod
    def create_client(user, data: Dict[str, Any]) -> Client:
        try:
            client = Client.objects.create(
                user=user,
                name=data.get('name', ''),
                email=data.get('email', ''),
                phone=data.get('phone', ''),
                address=data.get('address', ''),
                company_name=data.get('company_name', ''),
                tax_id=data.get('tax_id', ''),
                notes=data.get('notes', ''),
            )
            logger.info(f"Client {client.name} created successfully by user {user.username}")
            return client
        except Exception as e:
            logger.error(f"Error creating client: {str(e)}")
            raise ValidationError(f"Failed to create client: {str(e)}")
    
    @staticmethod
    def update_client(client: Client, data: Dict[str, Any]) -> Client:
        try:
            for field, value in data.items():
                if field not in ['id', 'user', 'created_at']:
                    setattr(client, field, value)
            client.save()
            logger.info(f"Client {client.name} updated successfully")
            return client
        except Exception as e:
            logger.error(f"Error updating client {client.id}: {str(e)}")
            raise ValidationError(f"Failed to update client: {str(e)}")
    
    @staticmethod
    def delete_client(client: Client, force: bool = False):
        invoices_count = client.invoices.count()
        
        if invoices_count > 0 and not force:
            raise ValidationError(
                f"Cannot delete client with {invoices_count} associated invoices. "
                "Set force=True to proceed anyway."
            )
        
        client_name = client.name
        client.delete()
        logger.info(f"Client {client_name} deleted successfully")
    
    @staticmethod
    def get_client_stats(client: Client) -> Dict[str, Any]:
        invoices = client.invoices.all()
        
        return {
            'total_invoices': invoices.count(),
            'paid_invoices': invoices.filter(status='paid').count(),
            'pending_invoices': invoices.filter(status__in=['sent', 'draft']).count(),
            'overdue_invoices': invoices.filter(status='overdue').count(),
            'total_revenue': invoices.filter(status='paid').aggregate(
                total=models.Sum('total_amount'))['total'] or Decimal('0.00'),
            'pending_revenue': invoices.filter(
                status__in=['sent', 'draft']).aggregate(
                total=models.Sum('total_amount'))['total'] or Decimal('0.00'),
        }
    
    @staticmethod
    def search_clients(user, query: str):
        from django.db.models import Q
        
        return Client.objects.filter(
            user=user
        ).filter(
            Q(name__icontains=query) |
            Q(email__icontains=query) |
            Q(company_name__icontains=query) |
            Q(phone__icontains=query)
        ).order_by('name')


from django.db import models
from decimal import Decimal
