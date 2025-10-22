import csv
from io import BytesIO, StringIO
from django.http import HttpResponse
from django.utils import timezone


class ExportService:
    @staticmethod
    def export_invoices_csv(invoices):
        """Export invoices to CSV format."""
        output = StringIO()
        writer = csv.writer(output)
        
        writer.writerow([
            'Invoice ID', 'Business Name', 'Client Name', 'Client Email',
            'Amount', 'Currency', 'Status', 'Issue Date', 'Due Date',
            'Paid Date', 'Created At'
        ])
        
        for invoice in invoices:
            writer.writerow([
                invoice.invoice_id,
                invoice.business_name,
                invoice.client_name,
                invoice.client_email,
                str(invoice.total_amount),
                invoice.currency,
                invoice.get_status_display(),
                invoice.issue_date.strftime('%Y-%m-%d') if invoice.issue_date else '',
                invoice.due_date.strftime('%Y-%m-%d') if invoice.due_date else '',
                invoice.paid_date.strftime('%Y-%m-%d') if invoice.paid_date else '',
                invoice.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            ])
        
        response = HttpResponse(output.getvalue().encode('utf-8'), content_type='text/csv; charset=utf-8')
        filename = f'invoices_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
    
    @staticmethod
    def export_payments_csv(payments):
        """Export payment transactions to CSV format."""
        output = StringIO()
        writer = csv.writer(output)
        
        writer.writerow([
            'Reference', 'Invoice ID', 'Amount', 'Currency', 'Status',
            'Payment Method', 'Paid By', 'Payment Email', 'Payment Date', 'Created At'
        ])
        
        for payment in payments:
            writer.writerow([
                payment.transaction_reference,
                payment.invoice.invoice_id,
                str(payment.amount),
                payment.currency,
                payment.get_status_display(),
                payment.get_payment_method_display(),
                payment.paid_by,
                payment.payment_email,
                payment.payment_date.strftime('%Y-%m-%d %H:%M:%S') if payment.payment_date else '',
                payment.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            ])
        
        response = HttpResponse(output.getvalue().encode('utf-8'), content_type='text/csv; charset=utf-8')
        filename = f'payments_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
    
    @staticmethod
    def export_clients_csv(clients):
        """Export clients to CSV format."""
        output = StringIO()
        writer = csv.writer(output)
        
        writer.writerow([
            'Name', 'Email', 'Phone', 'Company Name', 'Address',
            'Tax ID', 'Total Invoices', 'Total Revenue', 'Created At'
        ])
        
        for client in clients:
            writer.writerow([
                client.name,
                client.email,
                client.phone,
                client.company_name,
                client.address,
                client.tax_id,
                client.total_invoices,
                str(client.total_revenue),
                client.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            ])
        
        response = HttpResponse(output.getvalue().encode('utf-8'), content_type='text/csv; charset=utf-8')
        filename = f'clients_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
