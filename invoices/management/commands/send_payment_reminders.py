from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from invoices.models import Invoice
from invoices.services.notification_service import NotificationService
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Send payment reminders for overdue and upcoming invoices'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days-before',
            type=int,
            default=3,
            help='Send reminders for invoices due in N days'
        )

    def handle(self, *args, **options):
        days_before = options['days_before']
        today = timezone.now().date()
        upcoming_date = today + timedelta(days=days_before)
        
        overdue_invoices = Invoice.objects.filter(
            status='overdue',
            client_email__isnull=False
        ).exclude(client_email='')
        
        upcoming_invoices = Invoice.objects.filter(
            status__in=['sent', 'draft'],
            due_date=upcoming_date,
            client_email__isnull=False
        ).exclude(client_email='')
        
        sent_count = 0
        failed_count = 0
        
        self.stdout.write('Sending payment reminders...')
        
        for invoice in overdue_invoices:
            try:
                NotificationService.send_payment_reminder(invoice)
                sent_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Sent reminder for overdue invoice {invoice.invoice_id}')
                )
            except Exception as e:
                failed_count += 1
                self.stdout.write(
                    self.style.ERROR(f'Failed to send reminder for {invoice.invoice_id}: {str(e)}')
                )
        
        for invoice in upcoming_invoices:
            try:
                NotificationService.send_payment_reminder(invoice)
                sent_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Sent reminder for upcoming invoice {invoice.invoice_id}')
                )
            except Exception as e:
                failed_count += 1
                self.stdout.write(
                    self.style.ERROR(f'Failed to send reminder for {invoice.invoice_id}: {str(e)}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nSent {sent_count} reminder(s), {failed_count} failed'
            )
        )
