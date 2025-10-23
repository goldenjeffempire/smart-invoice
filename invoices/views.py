# invoices/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.urls import reverse
from django.core.mail import EmailMessage
from django.conf import settings
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db.models import Q
from io import BytesIO
from xhtml2pdf import pisa
from decimal import Decimal
import base64
import re

from .forms import InvoiceForm, SupportInquiryForm, ClientForm
from .models import Invoice, SupportInquiry, Client


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
@login_required
def invoice_list(request):
    """Display all invoices with filtering and search capabilities."""
    from django.core.paginator import Paginator
    from .analytics import AnalyticsService
    
    invoices = Invoice.objects.filter(user=request.user).select_related('client').order_by('-created_at')
    
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
    
    paginator = Paginator(invoices, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    analytics = AnalyticsService(request.user)
    revenue_metrics = analytics.get_revenue_metrics()
    recent_invoices = Invoice.objects.filter(user=request.user).select_related('client').order_by('-created_at')[:6]
    
    all_invoices = Invoice.objects.filter(user=request.user)
    
    context = {
        'invoices': page_obj,
        'page_obj': page_obj,
        'total_invoices': all_invoices.count(),
        'draft_count': all_invoices.filter(status='draft').count(),
        'sent_count': all_invoices.filter(status='sent').count(),
        'paid_count': all_invoices.filter(status='paid').count(),
        'overdue_count': all_invoices.filter(status='overdue').count(),
        'revenue_metrics': revenue_metrics,
        'recent_invoices': recent_invoices,
    }
    return render(request, 'invoices/invoice_list.html', context)


# ----------------------------
# Invoice Creation
# ----------------------------
@login_required
def create_invoice(request):
    """Create a new invoice with professional fields."""
    from .models import Client
    
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        if form.is_valid():
            invoice = form.save(commit=False)
            invoice.user = request.user
            
            if invoice.client_email:
                client, created = Client.objects.get_or_create(
                    user=request.user,
                    email=invoice.client_email,
                    defaults={
                        'name': invoice.client_name,
                        'phone': invoice.client_phone,
                        'address': invoice.client_address,
                    }
                )
                if not created and invoice.client_name:
                    client.name = invoice.client_name
                    client.phone = invoice.client_phone or client.phone
                    client.address = invoice.client_address or client.address
                    client.save()
                
                invoice.client = client
            
            invoice.save()
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
@login_required
def invoice_detail(request, pk):
    """View full invoice details with actions."""
    from .models import PaymentTransaction
    
    invoice = get_object_or_404(Invoice, pk=pk, user=request.user)
    payment_transactions = PaymentTransaction.objects.filter(invoice=invoice).order_by('-created_at')
    
    timeline_events = [
        {
            'date': invoice.created_at,
            'title': 'Invoice Created',
            'description': f'Invoice {invoice.invoice_id} was created',
            'icon': '📝',
            'type': 'created'
        },
    ]
    
    if invoice.status == 'sent' or invoice.status in ['paid', 'overdue', 'cancelled']:
        timeline_events.append({
            'date': invoice.updated_at if invoice.updated_at != invoice.created_at else invoice.created_at,
            'title': 'Invoice Sent',
            'description': f'Invoice sent to {invoice.client_name}',
            'icon': '📧',
            'type': 'sent'
        })
    
    if invoice.paid_date:
        timeline_events.append({
            'date': invoice.paid_date,
            'title': 'Payment Received',
            'description': f'Invoice marked as paid',
            'icon': '✅',
            'type': 'paid'
        })
    elif invoice.status == 'overdue' and invoice.due_date:
        from datetime import datetime
        timeline_events.append({
            'date': datetime.combine(invoice.due_date, datetime.min.time()),
            'title': 'Invoice Overdue',
            'description': 'Payment is overdue',
            'icon': '⚠️',
            'type': 'overdue'
        })
    
    for transaction in payment_transactions:
        timeline_events.append({
            'date': transaction.created_at,
            'title': f'Payment {transaction.status.title()}',
            'description': f'{transaction.currency} {transaction.amount} via {transaction.payment_method}',
            'icon': '💳',
            'type': 'payment'
        })
    
    timeline_events.sort(key=lambda x: x['date'])
    
    context = {
        'invoice': invoice,
        'payment_transactions': payment_transactions,
        'timeline_events': timeline_events,
    }
    
    return render(request, 'invoices/invoice_detail.html', context)


# ----------------------------
# Invoice Update
# ----------------------------
@login_required
def invoice_update(request, pk):
    """Update an existing invoice."""
    from .models import Client
    
    invoice = get_object_or_404(Invoice, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = InvoiceForm(request.POST, instance=invoice)
        if form.is_valid():
            invoice = form.save(commit=False)
            
            if invoice.client_email:
                client, created = Client.objects.get_or_create(
                    user=request.user,
                    email=invoice.client_email,
                    defaults={
                        'name': invoice.client_name,
                        'phone': invoice.client_phone,
                        'address': invoice.client_address,
                    }
                )
                if not created and invoice.client_name:
                    client.name = invoice.client_name
                    client.phone = invoice.client_phone or client.phone
                    client.address = invoice.client_address or client.address
                    client.save()
                
                invoice.client = client
            
            invoice.save()
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
@login_required
def invoice_update_status(request, pk):
    """Update invoice status."""
    if request.method == 'POST':
        invoice = get_object_or_404(Invoice, pk=pk, user=request.user)
        new_status = request.POST.get('status')
        
        # Get valid status choices
        valid_statuses = [choice[0] for choice in Invoice._meta.get_field('status').choices]
        
        if new_status in valid_statuses:
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
@login_required
def invoice_pdf(request, pk):
    """Download invoice as PDF."""
    invoice = get_object_or_404(Invoice, pk=pk, user=request.user)
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
@login_required
def send_invoice_email(request, pk):
    """Send invoice PDF via email."""
    invoice = get_object_or_404(Invoice, pk=pk, user=request.user)

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
@login_required
def send_invoice_whatsapp(request, pk):
    """Send invoice PDF via WhatsApp using Twilio."""
    invoice = get_object_or_404(Invoice, pk=pk, user=request.user)

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
    from .payment_service import PaystackService
    
    invoice = get_object_or_404(Invoice, pk=pk, user=request.user)
    
    if not settings.PAYSTACK_SECRET_KEY:
        messages.error(request, 'Payment system is not configured. Please contact support.')
        return redirect('invoice_detail', pk=pk)
    
    paystack = PaystackService()
    callback_url = request.build_absolute_uri(reverse('payment_callback'))
    
    result = paystack.initialize_transaction(invoice, callback_url)
    
    if result['success']:
        return redirect(result['authorization_url'])
    else:
        messages.error(request, f"Payment initialization failed: {result.get('message', 'Unknown error')}")
        return redirect('invoice_detail', pk=pk)


def payment_callback(request):
    """Handle Paystack payment callback and verify transaction."""
    from .payment_service import PaystackService
    
    reference = request.GET.get('reference')
    
    if not reference:
        messages.error(request, 'Invalid payment reference.')
        return redirect('invoice_list')
    
    paystack = PaystackService()
    verification = paystack.verify_transaction(reference)
    
    if verification['success'] and verification['status'] == 'success':
        result = paystack.process_payment_success(verification['data'])
        
        if result['success']:
            invoice = result['invoice']
            messages.success(request, f'Payment successful! Invoice {invoice.invoice_id} has been marked as paid.')
            return redirect('invoice_detail', pk=invoice.pk)
        else:
            messages.error(request, 'Error processing payment. Please contact support.')
            return redirect('invoice_list')
    else:
        messages.error(request, f'Payment verification failed: {verification.get("message", "Unknown error")}')
        return redirect('invoice_list')


def send_whatsapp_payment_link(request, pk):
    """Send WhatsApp message with Paystack payment link."""
    from .payment_service import PaystackService
    
    invoice = get_object_or_404(Invoice, pk=pk, user=request.user)
    
    if not invoice.client_phone:
        messages.error(request, 'No WhatsApp number provided for this client.')
        return redirect('invoice_detail', pk=pk)
    
    if not settings.PAYSTACK_SECRET_KEY:
        messages.error(request, 'Payment system is not configured.')
        return redirect('invoice_detail', pk=pk)
    
    paystack = PaystackService()
    callback_url = request.build_absolute_uri(reverse('payment_callback'))
    
    result = paystack.initialize_transaction(invoice, callback_url)
    
    if result['success']:
        payment_link = result['authorization_url']
        
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
        
        messages.success(request, 'Payment link generated! Opening WhatsApp...')
        return redirect(whatsapp_link)
    else:
        messages.error(request, f'Failed to generate payment link: {result.get("message", "Unknown error")}')
        return redirect('invoice_detail', pk=pk)


from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse


@csrf_exempt
def paystack_webhook(request):
    """Handle Paystack webhook notifications."""
    from .payment_service import PaystackService
    import json
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    signature = request.META.get('HTTP_X_PAYSTACK_SIGNATURE')
    if not signature:
        return JsonResponse({'error': 'No signature'}, status=400)
    
    payload = request.body.decode('utf-8')
    
    paystack = PaystackService()
    if not paystack.verify_webhook_signature(payload, signature):
        return JsonResponse({'error': 'Invalid signature'}, status=400)
    
    try:
        data = json.loads(payload)
        event = data.get('event')
        event_data = data.get('data', {})
        
        if event == 'charge.success':
            result = paystack.process_payment_success(event_data)
            if result['success']:
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'error': result.get('message')}, status=500)
        
        elif event == 'charge.failed':
            result = paystack.process_payment_failure(event_data)
            if result['success']:
                return JsonResponse({'status': 'acknowledged'})
            else:
                return JsonResponse({'error': result.get('message')}, status=500)
        
        return JsonResponse({'status': 'event_not_handled'})
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# ----------------------------
# Authentication Views
# ----------------------------
def signup_view(request):
    """User signup/registration view."""
    if request.user.is_authenticated:
        return redirect('invoice_list')
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome {user.username}! Your account has been created.')
            return redirect('invoice_list')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{error}')
    else:
        form = UserCreationForm()
    
    return render(request, 'invoices/signup.html', {'form': form})


def login_view(request):
    """User login view."""
    if request.user.is_authenticated:
        return redirect('invoice_list')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                next_url = request.GET.get('next', 'invoice_list')
                return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'invoices/login.html', {'form': form})


def logout_view(request):
    """User logout view."""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('landing')


# ----------------------------
# Analytics Dashboard
# ----------------------------
@login_required
def analytics_dashboard(request):
    """Display analytics dashboard with revenue metrics and insights."""
    import json
    from decimal import Decimal
    from .analytics import AnalyticsService
    
    def decimal_default(obj):
        if isinstance(obj, Decimal):
            return float(obj)
        raise TypeError
    
    analytics = AnalyticsService(request.user)
    dashboard_data = analytics.get_dashboard_summary()
    
    monthly_trend_json = json.dumps(dashboard_data.get('monthly_trend', []), default=decimal_default)
    invoice_stats_json = json.dumps(dashboard_data.get('invoice_statistics', {}), default=decimal_default)
    top_clients_json = json.dumps(dashboard_data.get('top_clients', []), default=decimal_default)
    payment_methods_json = json.dumps(dashboard_data.get('payment_methods', []), default=decimal_default)
    
    return render(request, 'invoices/analytics_dashboard.html', {
        'analytics': dashboard_data,
        'monthly_trend_json': monthly_trend_json,
        'invoice_stats_json': invoice_stats_json,
        'top_clients_json': top_clients_json,
        'payment_methods_json': payment_methods_json,
    })


# ----------------------------
# Export Functions
# ----------------------------
@login_required
def export_invoices(request):
    """Export invoices to CSV."""
    from .export_service import ExportService
    
    invoices = Invoice.objects.filter(user=request.user).order_by('-created_at')
    
    status_filter = request.GET.get('status')
    if status_filter:
        invoices = invoices.filter(status=status_filter)
    
    return ExportService.export_invoices_csv(invoices)


@login_required
def export_payments(request):
    """Export payment transactions to CSV."""
    from .export_service import ExportService
    from .models import PaymentTransaction
    
    payments = PaymentTransaction.objects.filter(
        invoice__user=request.user
    ).order_by('-created_at')
    
    return ExportService.export_payments_csv(payments)


@login_required
def export_clients(request):
    """Export clients to CSV."""
    from .export_service import ExportService
    from .models import Client
    
    clients = Client.objects.filter(user=request.user).order_by('name')
    
    return ExportService.export_clients_csv(clients)


# ========================================
# CLIENT MANAGEMENT VIEWS
# ========================================

@login_required
def client_list(request):
    """Display all clients with search and filter capabilities."""
    from .models import Client
    
    clients = Client.objects.filter(user=request.user)
    
    search_query = request.GET.get('q')
    if search_query:
        clients = clients.filter(
            Q(name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(company_name__icontains=search_query)
        )
    
    context = {
        'clients': clients,
        'total_clients': Client.objects.filter(user=request.user).count(),
    }
    return render(request, 'invoices/client_list.html', context)


@login_required
def client_create(request):
    """Create a new client."""
    from .forms import ClientForm
    
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            client = form.save(commit=False)
            client.user = request.user
            client.save()
            messages.success(request, f'Client "{client.name}" created successfully!')
            return redirect('client_list')
    else:
        form = ClientForm()
    
    return render(request, 'invoices/client_form.html', {'form': form})


@login_required
def client_update(request, pk):
    """Update an existing client."""
    from .models import Client
    from .forms import ClientForm
    
    client = get_object_or_404(Client, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            messages.success(request, f'Client "{client.name}" updated successfully!')
            return redirect('client_list')
    else:
        form = ClientForm(instance=client)
    
    return render(request, 'invoices/client_form.html', {'form': form, 'client': client})


@login_required
def client_detail(request, pk):
    """Display client details with related invoices."""
    from .models import Client
    
    client = get_object_or_404(Client, pk=pk, user=request.user)
    invoices = Invoice.objects.filter(client=client).order_by('-created_at')
    
    context = {
        'client': client,
        'invoices': invoices,
        'total_invoices': invoices.count(),
        'paid_invoices': invoices.filter(status='paid').count(),
        'pending_revenue': sum(inv.total_amount for inv in invoices.filter(status='sent')),
        'total_revenue': sum(inv.total_amount for inv in invoices.filter(status='paid')),
    }
    return render(request, 'invoices/client_detail.html', context)


@login_required
def client_delete(request, pk):
    """Delete a client."""
    from .models import Client
    
    client = get_object_or_404(Client, pk=pk, user=request.user)
    
    if request.method == 'POST':
        client_name = client.name
        client.delete()
        messages.success(request, f'Client "{client_name}" deleted successfully!')
        return redirect('client_list')
    
    return render(request, 'invoices/client_confirm_delete.html', {'client': client})
