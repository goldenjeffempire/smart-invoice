# invoices/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.urls import reverse
from .forms import InvoiceForm
from .models import Invoice
from io import BytesIO
from xhtml2pdf import pisa


def landing_page(request):
    # Auto-generate a sample invoice if none exist
    if not Invoice.objects.exists():
        # Custom invoice ID like INV-0001
        invoice_count = Invoice.objects.count() + 1
        invoice_id = f"INV-{invoice_count:04d}"

        sample_invoice = Invoice.objects.create(
            invoice_id=invoice_id,
            client_name="Acme Corp",
            client_email="client@acmecorp.com",
            item_description="Website Automation System (Full Stack + AI Integration)",
            amount=1200.00,
            due_date="2025-12-31",
        )
        sample_invoice.save()

    return render(request, 'invoices/landing.html')


def create_invoice(request):
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        if form.is_valid():
            # Auto-generate clean sequential IDs
            invoice_count = Invoice.objects.count() + 1
            invoice = form.save(commit=False)
            invoice.invoice_id = f"INV-{invoice_count:04d}"
            invoice.save()
            return redirect('invoice_detail', pk=invoice.pk)
    else:
        form = InvoiceForm()
    return render(request, 'invoices/invoice_form.html', {'form': form})

def invoice_preview(request):
    """Show a dummy sample invoice so users always see something nice."""
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

def invoice_detail(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    return render(request, 'invoices/invoice_detail.html', {'invoice': invoice})


def invoice_pdf(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    html = render_to_string('invoices/invoice_pdf.html', {'invoice': invoice})
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    if not pdf.err:
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        filename = f"{invoice.invoice_id}.pdf"
        content = f"attachment; filename={filename}"
        response['Content-Disposition'] = content
        return response
    return HttpResponse("Error generating PDF", status=500)
