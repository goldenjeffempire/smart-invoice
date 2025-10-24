"""
Generate monthly invoice reports and send to business owners.
Run with: python manage.py generate_invoice_reports --month 10 --year 2025
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Sum, Count, Q
from invoices.models import Invoice
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Generate monthly invoice reports for users'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--month',
            type=int,
            default=timezone.now().month,
            help='Month number (1-12)'
        )
        parser.add_argument(
            '--year',
            type=int,
            default=timezone.now().year,
            help='Year (e.g., 2025)'
        )
        parser.add_argument(
            '--email',
            action='store_true',
            help='Email reports to users'
        )
    
    def handle(self, *args, **options):
        month = options['month']
        year = options['year']
        send_email = options['email']
        
        self.stdout.write(f'Generating reports for {year}-{month:02d}')
        
        invoices = Invoice.objects.filter(
            created_at__year=year,
            created_at__month=month
        ).select_related('user')
        
        users = invoices.values('user').distinct()
        
        for user_dict in users:
            user_id = user_dict['user']
            user_invoices = invoices.filter(user_id=user_id)
            
            report = self.generate_user_report(user_invoices, month, year)
            
            self.stdout.write(f"\n{report}")
            
            if send_email and user_invoices.first().user.email:
                self.email_report(user_invoices.first().user, report, month, year)
    
    def generate_user_report(self, invoices, month, year):
        """Generate text report for user's monthly invoices."""
        month_name = datetime(year, month, 1).strftime('%B %Y')
        
        stats = invoices.aggregate(
            total_invoices=Count('id'),
            total_revenue=Sum('total_amount', filter=Q(status='paid')),
            total_pending=Sum('total_amount', filter=Q(status__in=['sent', 'draft'])),
            paid_count=Count('id', filter=Q(status='paid')),
            overdue_count=Count('id', filter=Q(status='overdue'))
        )
        
        report = f"""
════════════════════════════════════════
   MONTHLY INVOICE REPORT - {month_name}
════════════════════════════════════════

📊 Summary Statistics:
   • Total Invoices: {stats['total_invoices']}
   • Paid Invoices: {stats['paid_count']}
   • Overdue Invoices: {stats['overdue_count']}
   
💰 Revenue:
   • Total Revenue (Paid): ${stats['total_revenue'] or 0:.2f}
   • Pending Payments: ${stats['total_pending'] or 0:.2f}

════════════════════════════════════════
        """
        return report
    
    def email_report(self, user, report, month, year):
        """Email the report to the user."""
        month_name = datetime(year, month, 1).strftime('%B %Y')
        
        try:
            send_mail(
                subject=f'Your Smart Invoice Monthly Report - {month_name}',
                message=report,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False
            )
            self.stdout.write(self.style.SUCCESS(f'✓ Emailed report to {user.email}'))
        except Exception as e:
            logger.error(f'Failed to email report to {user.email}: {str(e)}')
            self.stdout.write(self.style.ERROR(f'✗ Failed to email to {user.email}'))
