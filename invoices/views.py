# invoices/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.urls import reverse
from django.core.mail import EmailMessage
from django.conf import settings
from io import BytesIO
from xhtml2pdf import pisa

from .forms import InvoiceForm
from .models import Invoice


# ----------------------------
# PDF Utility
# ----------------------------
def _render_invoice_pdf(invoice):
    """Generate and return PDF bytes for an invoice."""
    html = render_to_string('invoices/invoice_pdf.html', {'invoice': invoice})
    result = BytesIO()
    pisa_status = pisa.pisaDocument(BytesIO(html.encode('UTF-8')), result)
    if pisa_status.err:
        return None
    return result.getvalue()


# ----------------------------
# Landing Page
# ----------------------------
def landing_page(request):
    """Show landing page with a sample invoice if none exist."""
    if not Invoice.objects.exists():
        invoice_count = Invoice.objects.count() + 1
        invoice_id = f"INV-{invoice_count:04d}"
        Invoice.objects.create(
            invoice_id=invoice_id,
            client_name="Acme Corp",
            client_email="client@acmecorp.com",
            item_description="Website Automation System (Full Stack + AI Integration)",
            amount=1200.00,
            due_date="2025-12-31",
        )
    return render(request, 'invoices/landing.html')


# ----------------------------
# Invoice Creation
# ----------------------------
def create_invoice(request):
    """Create a new invoice with sequential invoice ID."""
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        if form.is_valid():
            invoice_count = Invoice.objects.count() + 1
            invoice = form.save(commit=False)
            invoice.invoice_id = f"INV-{invoice_count:04d}"
            invoice.save()
            return redirect('invoice_detail', pk=invoice.pk)
    else:
        form = InvoiceForm()
    return render(request, 'invoices/invoice_form.html', {'form': form})


# ----------------------------
# Invoice Detail
# ----------------------------
def invoice_detail(request, pk):
    """View full invoice details."""
    invoice = get_object_or_404(Invoice, pk=pk)
    return render(request, 'invoices/invoice_detail.html', {'invoice': invoice})


# ----------------------------
# PDF Generation
# ----------------------------
def invoice_pdf(request, pk):
    """Download invoice as PDF."""
    invoice = get_object_or_404(Invoice, pk=pk)
    pdf_bytes = _render_invoice_pdf(invoice)
    if pdf_bytes:
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        filename = f"{invoice.invoice_id}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    return HttpResponse("Error generating PDF", status=500)


# ----------------------------
# Send Invoice via Email
# ----------------------------
def send_invoice_email(request, pk):
    """Send invoice PDF via email."""
    invoice = get_object_or_404(Invoice, pk=pk)

    if request.method == 'POST':
        to_email = request.POST.get('to_email') or getattr(invoice, 'client_email_or_whatsapp', None)
        if not to_email:
            return render(request, 'invoices/invoice_detail.html', {
                'invoice': invoice,
                'error': 'No recipient provided.'
            })

        pdf_bytes = _render_invoice_pdf(invoice)
        if not pdf_bytes:
            return render(request, 'invoices/invoice_detail.html', {
                'invoice': invoice,
                'error': 'Could not generate PDF.'
            })

        subject = f"Invoice {invoice.invoice_id} from {invoice.business_name}"
        body = (
            f"Hello,\n\nPlease find attached the invoice {invoice.invoice_id} for {invoice.business_name}.\n\n"
            f"Regards,\n{invoice.business_name}\n\n"
            "Built by Jeffery Onome — onome-portfolio-ten.vercel.app"
        )

        email = EmailMessage(subject, body, settings.EMAIL_HOST_USER, [to_email])
        email.attach(f"{invoice.invoice_id}.pdf", pdf_bytes, 'application/pdf')

        try:
            email.send(fail_silently=False)
            return render(request, 'invoices/invoice_detail.html', {
                'invoice': invoice,
                'success': f'Email sent to {to_email}.'
            })
        except Exception as e:
            return render(request, 'invoices/invoice_detail.html', {
                'invoice': invoice,
                'error': f'Failed to send email: {e}'
            })
    else:
        # Simple GET fallback
        return render(request, 'invoices/invoice_detail.html', {'invoice': invoice})


# ----------------------------
# Invoice Preview (Optional Demo)
# ----------------------------
def invoice_preview(request):
    """Preview a dummy invoice (for demo or design)."""
    dummy_data = {
        'client_name': 'Acme Corp.',
        'invoice_number': 'INV-001',
        'date': '2025-10-21',
        'due_date': '2025-11-01',
        'items': [
            {'description': 'Website Development', 'quantity': 1, 'price': 1200},
            {'description': 'Hosting (3 months)', 'quantity': 1, 'price': 90},
        ],
        'total': 1290,
        'status': 'Pending',
    }
    return render(request, 'invoices/sample_invoice.html', dummy_data)
