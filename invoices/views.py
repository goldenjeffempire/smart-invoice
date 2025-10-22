# invoices/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.urls import reverse
from django.core.mail import EmailMessage
from django.conf import settings
from django.utils import timezone
from django.contrib import messages
from django.db.models import Q
from io import BytesIO
from xhtml2pdf import pisa
from decimal import Decimal
import base64
import re

from .forms import InvoiceForm, SupportInquiryForm
from .models import Invoice, SupportInquiry


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
    """Show modern landing page for Smart Invoice platform."""
    return render(request, 'invoices/landing.html')


# ----------------------------
# Invoice Dashboard/List
# ----------------------------
def invoice_list(request):
    """Display all invoices with filtering and search capabilities."""
    invoices = Invoice.objects.all()
    
    status_filter = request.GET.get('status')
    if status_filter:
        invoices = invoices.filter(status=status_filter)
    
    search_query = request.GET.get('q')
    if search_query:
        invoices = invoices.filter(
            Q(invoice_id__icontains=search_query) |
            Q(client_name__icontains=search_query) |
            Q(business_name__icontains=search_query)
        )
    
    context = {
        'invoices': invoices,
        'total_invoices': Invoice.objects.count(),
        'draft_count': Invoice.objects.filter(status='draft').count(),
        'sent_count': Invoice.objects.filter(status='sent').count(),
        'paid_count': Invoice.objects.filter(status='paid').count(),
        'overdue_count': Invoice.objects.filter(status='overdue').count(),
    }
    return render(request, 'invoices/invoice_list.html', context)


# ----------------------------
# Invoice Creation
# ----------------------------
def create_invoice(request):
    """Create a new invoice with professional fields."""
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        if form.is_valid():
            invoice = form.save()
            messages.success(request, f'Invoice {invoice.invoice_id} created successfully!')
            return redirect('invoice_detail', pk=invoice.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = InvoiceForm()
    
    return render(request, 'invoices/invoice_form.html', {'form': form})


# ----------------------------
# Invoice Detail
# ----------------------------
def invoice_detail(request, pk):
    """View full invoice details with actions."""
    invoice = get_object_or_404(Invoice, pk=pk)
    return render(request, 'invoices/invoice_detail.html', {'invoice': invoice})


# ----------------------------
# Invoice Update
# ----------------------------
def invoice_update(request, pk):
    """Update an existing invoice."""
    invoice = get_object_or_404(Invoice, pk=pk)
    
    if request.method == 'POST':
        form = InvoiceForm(request.POST, instance=invoice)
        if form.is_valid():
            invoice = form.save()
            messages.success(request, f'Invoice {invoice.invoice_id} updated successfully!')
            return redirect('invoice_detail', pk=invoice.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = InvoiceForm(instance=invoice)
    
    return render(request, 'invoices/invoice_form.html', {'form': form, 'invoice': invoice})


# ----------------------------
# Invoice Status Update
# ----------------------------
def invoice_update_status(request, pk):
    """Update invoice status."""
    if request.method == 'POST':
        invoice = get_object_or_404(Invoice, pk=pk)
        new_status = request.POST.get('status')
        
        if new_status in dict(Invoice._meta.get_field('status').choices):
            invoice.status = new_status
            if new_status == 'paid':
                invoice.paid_date = timezone.now().date()
            invoice.save()
            messages.success(request, f'Invoice status updated to {invoice.get_status_display()}')
        else:
            messages.error(request, 'Invalid status')
        
        return redirect('invoice_detail', pk=pk)
    
    return redirect('invoice_list')


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
    
    messages.error(request, 'Error generating PDF')
    return redirect('invoice_detail', pk=pk)


# ----------------------------
# Send Invoice via Email
# ----------------------------
def send_invoice_email(request, pk):
    """Send invoice PDF via email."""
    invoice = get_object_or_404(Invoice, pk=pk)

    if request.method == 'POST':
        to_email = request.POST.get('to_email') or invoice.client_email
        
        if not to_email:
            messages.error(request, 'No recipient email provided.')
            return redirect('invoice_detail', pk=pk)

        pdf_bytes = _render_invoice_pdf(invoice)
        if not pdf_bytes:
            messages.error(request, 'Could not generate PDF.')
            return redirect('invoice_detail', pk=pk)

        subject = f"Invoice {invoice.invoice_id} from {invoice.business_name}"
        body = f"""Hello {invoice.client_name},

Please find attached Invoice {invoice.invoice_id} for the amount of {invoice.currency} {invoice.total_amount}.

Invoice Details:
- Issue Date: {invoice.issue_date}
- Due Date: {invoice.due_date if invoice.due_date else 'Upon receipt'}
- Amount: {invoice.currency} {invoice.total_amount}

{invoice.payment_instructions if invoice.payment_instructions else ''}

Thank you for your business!

Best regards,
{invoice.business_name}
"""

        email = EmailMessage(subject, body, settings.EMAIL_HOST_USER, [to_email])
        email.attach(f"{invoice.invoice_id}.pdf", pdf_bytes, 'application/pdf')

        try:
            email.send(fail_silently=False)
            invoice.status = 'sent'
            invoice.save()
            messages.success(request, f'Invoice sent successfully to {to_email}!')
        except Exception as e:
            messages.error(request, f'Failed to send email: {str(e)}')
        
        return redirect('invoice_detail', pk=pk)
    
    return redirect('invoice_detail', pk=pk)


# ----------------------------
# Send Invoice via WhatsApp
# ----------------------------
def send_invoice_whatsapp(request, pk):
    """Send invoice PDF via WhatsApp using Twilio."""
    invoice = get_object_or_404(Invoice, pk=pk)

    if request.method == 'POST':
        whatsapp_number = request.POST.get('whatsapp_number') or invoice.client_phone
        
        if not whatsapp_number:
            messages.error(request, 'No WhatsApp number provided.')
            return redirect('invoice_detail', pk=pk)

        whatsapp_number = _normalize_phone_number(whatsapp_number)

        if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
            messages.error(request, 'WhatsApp functionality is not configured. Please set up Twilio credentials.')
            return redirect('invoice_detail', pk=pk)

        pdf_bytes = _render_invoice_pdf(invoice)
        if not pdf_bytes:
            messages.error(request, 'Could not generate PDF.')
            return redirect('invoice_detail', pk=pk)

        try:
            from twilio.rest import Client
            
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            media_url = _create_public_pdf_url(request, invoice, pdf_bytes)

            message_body = (
                f"📄 *Invoice {invoice.invoice_id}*\n\n"
                f"From: {invoice.business_name}\n"
                f"Amount: {invoice.currency} {invoice.total_amount}\n"
                f"Due: {invoice.due_date if invoice.due_date else 'Upon receipt'}\n\n"
                f"Please find your invoice attached.\n\n"
                f"Thank you for your business!"
            )

            message = client.messages.create(
                body=message_body,
                from_=settings.TWILIO_WHATSAPP_NUMBER,
                to=f'whatsapp:{whatsapp_number}',
                media_url=[media_url] if media_url else None
            )

            invoice.status = 'sent'
            invoice.save()
            messages.success(request, f'Invoice sent via WhatsApp to {whatsapp_number}!')
            
        except ImportError:
            messages.error(request, 'Twilio package not installed.')
        except Exception as e:
            messages.error(request, f'Failed to send WhatsApp message: {str(e)}')
        
        return redirect('invoice_detail', pk=pk)
    
    return redirect('invoice_detail', pk=pk)


# ----------------------------
# Utility Functions
# ----------------------------
def _normalize_phone_number(phone):
    """Normalize phone number to E.164 format."""
    phone = re.sub(r'[^\d+]', '', phone)
    
    if phone.startswith('+'):
        return phone
    elif phone.startswith('00'):
        return '+' + phone[2:]
    elif len(phone) == 10:
        return '+1' + phone
    elif len(phone) == 11 and phone.startswith('1'):
        return '+' + phone
    else:
        return '+' + phone


def _create_public_pdf_url(request, invoice, pdf_bytes):
    """
    Create a publicly accessible URL for the PDF.
    In production, upload to cloud storage (S3, Cloudinary, etc.)
    For now, we return the direct PDF URL.
    """
    pdf_url = request.build_absolute_uri(reverse('invoice_pdf', args=[invoice.pk]))
    return pdf_url


# ----------------------------
# Invoice Preview (Demo)
# ----------------------------
def invoice_preview(request):
    """Preview a sample invoice for demo purposes."""
    dummy_invoice = Invoice(
        invoice_id='DEMO-001',
        business_name='Smart Invoice Inc.',
        business_email='hello@smartinvoice.com',
        client_name='Acme Corporation',
        client_email='billing@acme.com',
        description='Professional Invoice Management System',
        quantity=Decimal('1.00'),
        unit_price=Decimal('1299.00'),
        tax_rate=Decimal('10.00'),
        discount_amount=Decimal('0.00'),
        currency='USD',
        status='draft',
        payment_terms='net_30',
        issue_date=timezone.now().date(),
    )
    dummy_invoice.save = lambda: None
    
    return render(request, 'invoices/invoice_pdf.html', {'invoice': dummy_invoice})


# ----------------------------
# FAQ Page
# ----------------------------
def faq_page(request):
    """Display FAQ page."""
    return render(request, 'invoices/faq.html')


# ----------------------------
# Support Page
# ----------------------------
def support_page(request):
    """Handle support inquiries."""
    if request.method == 'POST':
        form = SupportInquiryForm(request.POST)
        if form.is_valid():
            inquiry = form.save()
            
            try:
                subject = f"New Support Inquiry: {inquiry.subject}"
                body = f"""New support inquiry received:

Name: {inquiry.name}
Email: {inquiry.email}
Subject: {inquiry.subject}

Message:
{inquiry.message}

---
Submitted at: {inquiry.created_at}
"""
                admin_email = settings.EMAIL_HOST_USER or 'support@smartinvoice.com'
                email = EmailMessage(subject, body, inquiry.email, [admin_email])
                email.send(fail_silently=True)
            except Exception:
                pass
            
            messages.success(request, 'Thank you for contacting us! We have received your message and will respond within 24 hours.')
            return redirect('support')
        else:
            messages.error(request, 'Please correct the errors in the form.')
    else:
        form = SupportInquiryForm()
    
    return render(request, 'invoices/support.html', {'form': form})


# ----------------------------
# Payment Integration
# ----------------------------
def initialize_paystack_payment(request, pk):
    """Initialize Paystack transaction and redirect to payment page."""
    import requests
    import json
    
    invoice = get_object_or_404(Invoice, pk=pk)
    
    if not settings.PAYSTACK_SECRET_KEY:
        messages.error(request, 'Payment system is not configured. Please contact support.')
        return redirect('invoice_detail', pk=pk)
    
    amount_in_kobo = int(invoice.total_amount * 100)
    
    headers = {
        'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
        'Content-Type': 'application/json',
    }
    
    callback_url = request.build_absolute_uri(reverse('payment_callback'))
    
    payload = {
        'amount': amount_in_kobo,
        'email': invoice.client_email or 'customer@example.com',
        'reference': invoice.invoice_id,
        'currency': invoice.currency,
        'callback_url': callback_url,
        'metadata': {
            'invoice_id': invoice.invoice_id,
            'business_name': invoice.business_name,
            'client_name': invoice.client_name,
        }
    }
    
    try:
        response = requests.post(
            'https://api.paystack.co/transaction/initialize',
            headers=headers,
            data=json.dumps(payload),
            timeout=10
        )
        
        response_data = response.json()
        
        if response_data.get('status') and response_data.get('data'):
            authorization_url = response_data['data']['authorization_url']
            reference = response_data['data']['reference']
            
            invoice.paystack_reference = reference
            invoice.save()
            
            return redirect(authorization_url)
        else:
            messages.error(request, f"Payment initialization failed: {response_data.get('message', 'Unknown error')}")
            return redirect('invoice_detail', pk=pk)
            
    except requests.exceptions.RequestException as e:
        messages.error(request, f'Payment system error: {str(e)}')
        return redirect('invoice_detail', pk=pk)


def payment_callback(request):
    """Handle Paystack payment callback."""
    reference = request.GET.get('reference')
    
    if not reference:
        messages.error(request, 'Invalid payment reference.')
        return redirect('invoice_list')
    
    try:
        invoice = Invoice.objects.get(paystack_reference=reference)
        invoice.status = 'paid'
        invoice.paid_date = timezone.now().date()
        invoice.save()
        
        messages.success(request, f'Payment successful! Invoice {invoice.invoice_id} has been marked as paid.')
        return redirect('invoice_detail', pk=invoice.pk)
    except Invoice.DoesNotExist:
        messages.error(request, 'Invoice not found.')
        return redirect('invoice_list')


def send_whatsapp_payment_link(request, pk):
    """Send WhatsApp message with Paystack payment link."""
    import requests
    import json
    
    invoice = get_object_or_404(Invoice, pk=pk)
    
    if not invoice.client_phone:
        messages.error(request, 'No WhatsApp number provided for this client.')
        return redirect('invoice_detail', pk=pk)
    
    if not settings.PAYSTACK_SECRET_KEY:
        messages.error(request, 'Payment system is not configured.')
        return redirect('invoice_detail', pk=pk)
    
    amount_in_kobo = int(invoice.total_amount * 100)
    
    headers = {
        'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
        'Content-Type': 'application/json',
    }
    
    callback_url = request.build_absolute_uri(reverse('payment_callback'))
    
    payload = {
        'amount': amount_in_kobo,
        'email': invoice.client_email or 'customer@example.com',
        'reference': f"{invoice.invoice_id}-{timezone.now().timestamp()}",
        'currency': invoice.currency,
        'callback_url': callback_url,
        'metadata': {
            'invoice_id': invoice.invoice_id,
            'business_name': invoice.business_name,
            'client_name': invoice.client_name,
        }
    }
    
    try:
        response = requests.post(
            'https://api.paystack.co/transaction/initialize',
            headers=headers,
            data=json.dumps(payload),
            timeout=10
        )
        
        response_data = response.json()
        
        if response_data.get('status') and response_data.get('data'):
            payment_link = response_data['data']['authorization_url']
            
            client_phone = invoice.client_phone.strip()
            if client_phone.startswith('+'):
                whatsapp_number = client_phone[1:]
            else:
                whatsapp_number = client_phone.replace(' ', '').replace('-', '')
            
            message = f"💰 *Invoice {invoice.invoice_id}*%0A%0A"
            message += f"From: {invoice.business_name}%0A"
            message += f"Amount: {invoice.currency} {invoice.total_amount}%0A"
            message += f"Due: {invoice.due_date if invoice.due_date else 'Upon receipt'}%0A%0A"
            message += f"Click here to pay securely:%0A{payment_link}%0A%0A"
            message += f"Thank you for your business!"
            
            whatsapp_link = f"https://wa.me/{whatsapp_number}?text={message}"
            
            return redirect(whatsapp_link)
        else:
            messages.error(request, 'Failed to generate payment link.')
            return redirect('invoice_detail', pk=pk)
            
    except requests.exceptions.RequestException as e:
        messages.error(request, f'Payment system error: {str(e)}')
        return redirect('invoice_detail', pk=pk)
