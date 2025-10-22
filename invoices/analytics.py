from django.db.models import Sum, Count, Avg, Q, F
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta
from .models import Invoice, PaymentTransaction, Client


class AnalyticsService:
    def __init__(self, user):
        self.user = user
    
    def get_revenue_metrics(self):
        """Calculate revenue metrics for the user."""
        invoices = Invoice.objects.filter(user=self.user)
        
        total_revenue = invoices.filter(status='paid').aggregate(
            total=Sum('total_amount')
        )['total'] or Decimal('0.00')
        
        pending_revenue = invoices.filter(
            status__in=['sent', 'draft', 'overdue']
        ).aggregate(
            total=Sum('total_amount')
        )['total'] or Decimal('0.00')
        
        overdue_revenue = invoices.filter(status='overdue').aggregate(
            total=Sum('total_amount')
        )['total'] or Decimal('0.00')
        
        return {
            'total_revenue': total_revenue,
            'pending_revenue': pending_revenue,
            'overdue_revenue': overdue_revenue,
        }
    
    def get_invoice_statistics(self):
        """Get invoice counts by status."""
        invoices = Invoice.objects.filter(user=self.user)
        
        total_invoices = invoices.count()
        draft_count = invoices.filter(status='draft').count()
        sent_count = invoices.filter(status='sent').count()
        paid_count = invoices.filter(status='paid').count()
        overdue_count = invoices.filter(status='overdue').count()
        cancelled_count = invoices.filter(status='cancelled').count()
        
        payment_rate = (paid_count / total_invoices * 100) if total_invoices > 0 else 0
        
        avg_invoice_value = invoices.aggregate(
            avg=Avg('total_amount')
        )['avg'] or Decimal('0.00')
        
        return {
            'total_invoices': total_invoices,
            'draft_count': draft_count,
            'sent_count': sent_count,
            'paid_count': paid_count,
            'overdue_count': overdue_count,
            'cancelled_count': cancelled_count,
            'payment_rate': round(payment_rate, 2),
            'avg_invoice_value': avg_invoice_value,
        }
    
    def get_monthly_revenue_trend(self, months=6):
        """Get revenue trend for the last N months using calendar months."""
        from django.db.models.functions import TruncMonth
        from dateutil.relativedelta import relativedelta
        
        today = timezone.now().date()
        start_date = today - relativedelta(months=months-1)
        start_date = start_date.replace(day=1)
        
        invoices = Invoice.objects.filter(
            user=self.user,
            status='paid',
            paid_date__gte=start_date
        ).annotate(
            month=TruncMonth('paid_date')
        ).values('month').annotate(
            revenue=Sum('total_amount'),
            count=Count('id')
        ).order_by('month')
        
        month_dict = {item['month'].strftime('%Y-%m'): item for item in invoices}
        
        monthly_data = []
        current = start_date
        for i in range(months):
            month_key = current.strftime('%Y-%m')
            data = month_dict.get(month_key, {'revenue': Decimal('0.00'), 'count': 0})
            
            monthly_data.append({
                'month': current.strftime('%B %Y'),
                'revenue': float(data.get('revenue', Decimal('0.00'))),
                'invoices': data.get('count', 0)
            })
            
            current = current + relativedelta(months=1)
        
        return monthly_data
    
    def get_top_clients(self, limit=5):
        """Get top clients by revenue."""
        clients = Client.objects.filter(user=self.user).annotate(
            total_revenue=Sum(
                'invoices__total_amount',
                filter=Q(invoices__status='paid')
            ),
            total_invoices=Count('invoices')
        ).order_by('-total_revenue')[:limit]
        
        return [
            {
                'name': client.name,
                'email': client.email,
                'total_revenue': client.total_revenue or Decimal('0.00'),
                'total_invoices': client.total_invoices,
            }
            for client in clients
        ]
    
    def get_payment_method_breakdown(self):
        """Get breakdown of payments by method."""
        payments = PaymentTransaction.objects.filter(
            invoice__user=self.user,
            status='successful'
        )
        
        breakdown = payments.values('payment_method').annotate(
            count=Count('id'),
            total=Sum('amount')
        ).order_by('-total')
        
        return list(breakdown)
    
    def get_recent_activity(self, limit=10):
        """Get recent invoice and payment activity."""
        recent_invoices = Invoice.objects.filter(user=self.user).order_by('-created_at')[:limit]
        
        activities = []
        for invoice in recent_invoices:
            activities.append({
                'type': 'invoice',
                'invoice_id': invoice.invoice_id,
                'client_name': invoice.client_name,
                'amount': invoice.total_amount,
                'status': invoice.status,
                'date': invoice.created_at,
            })
        
        return activities
    
    def get_dashboard_summary(self):
        """Get comprehensive dashboard summary."""
        return {
            'revenue_metrics': self.get_revenue_metrics(),
            'invoice_statistics': self.get_invoice_statistics(),
            'monthly_trend': self.get_monthly_revenue_trend(),
            'top_clients': self.get_top_clients(),
            'payment_methods': self.get_payment_method_breakdown(),
            'recent_activity': self.get_recent_activity(),
        }
