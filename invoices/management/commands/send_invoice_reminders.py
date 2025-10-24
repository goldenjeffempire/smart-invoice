"""
Django management command to send automated invoice payment reminders.
Run this with cron: python manage.py send_invoice_reminders
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from invoices.models import Invoice
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Send payment reminders for overdue invoices'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--days-overdue',
            type=int,
            default=3,
            help='Send reminders for invoices overdue by this many days'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be sent without actually sending'
        )
    
    def handle(self, *args, **options):
        days_overdue = options['days_overdue']
        dry_run = options['dry_run']
        
        now = timezone.now()
        cutoff_date = now - timezone.timedelta(days=days_overdue)
        
        overdue_invoices = Invoice.objects.filter(
            status='overdue',
            due_date__lte=cutoff_date,
            paid_date__isnull=True
        ).select_related('user', 'client')
        
        self.stdout.write(f'Found {overdue_invoices.count()} overdue invoices')
        
        sent_count = 0
        for invoice in overdue_invoices:
            if dry_run:
                self.stdout.write(
                    self.style.WARNING(
                        f'[DRY RUN] Would send reminder for {invoice.invoice_id} to {invoice.client_email}'
                    )
                )
            else:
                try:
                    self.send_reminder(invoice)
                    sent_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✓ Sent reminder for {invoice.invoice_id} to {invoice.client_email}'
                        )
                    )
                except Exception as e:
                    logger.error(f'Failed to send reminder for {invoice.invoice_id}: {str(e)}')
                    self.stdout.write(
                        self.style.ERROR(
                            f'✗ Failed to send reminder for {invoice.invoice_id}: {str(e)}'
                        )
                    )
        
        if not dry_run:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\nCompleted: Sent {sent_count}/{overdue_invoices.count()} reminders'
                )
            )
        else:
            self.stdout.write(self.style.WARNING('\nDRY RUN - No emails were sent'))
    
    def send_reminder(self, invoice):
        """Send payment reminder email for overdue invoice."""
        days_overdue = (timezone.now().date() - invoice.due_date).days
        
        subject = f'Payment Reminder: Invoice {invoice.invoice_id} is {days_overdue} days overdue'
        
        message = f"""
Dear {invoice.client_name},

This is a friendly reminder that your invoice is now {days_overdue} days overdue.

Invoice Details:
- Invoice Number: {invoice.invoice_id}
- Amount Due: {invoice.currency} {invoice.total_amount}
- Original Due Date: {invoice.due_date.strftime('%B %d, %Y')}
- Days Overdue: {days_overdue}

Please arrange payment at your earliest convenience to avoid any late fees.

You can pay online at: {settings.SITE_URL}/invoice/{invoice.pk}/pay/

If you have already made this payment, please disregard this reminder.

Thank you for your business.

Best regards,
{invoice.business_name}
{invoice.business_email}
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[invoice.client_email],
            fail_silently=False
        )
