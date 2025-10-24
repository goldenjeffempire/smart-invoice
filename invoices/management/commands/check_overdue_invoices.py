from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from invoices.services.invoice_service import InvoiceService
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Check and mark overdue invoices'

    def handle(self, *args, **options):
        self.stdout.write('Checking for overdue invoices...')
        
        total_marked = 0
        for user in User.objects.all():
            count = InvoiceService.check_overdue_invoices(user)
            total_marked += count
            
            if count > 0:
                self.stdout.write(
                    self.style.WARNING(
                        f'Marked {count} invoice(s) as overdue for user {user.username}'
                    )
                )
        
        if total_marked == 0:
            self.stdout.write(self.style.SUCCESS('No overdue invoices found'))
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully marked {total_marked} invoice(s) as overdue'
                )
            )
