from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Invoices
    path('invoices/', views.invoice_list, name='invoice_list'),
    path('invoice/create/', views.create_invoice, name='create_invoice'),
    path('invoice/<int:pk>/', views.invoice_detail, name='invoice_detail'),
    path('invoice/<int:pk>/edit/', views.invoice_update, name='invoice_update'),
    path('invoice/<int:pk>/status/', views.invoice_update_status, name='invoice_update_status'),
    path('invoice/<int:pk>/pdf/', views.invoice_pdf, name='invoice_pdf'),
    path('invoice/<int:pk>/send-email/', views.send_invoice_email, name='send_invoice_email'),
    path('invoice/<int:pk>/send-whatsapp/', views.send_invoice_whatsapp, name='send_invoice_whatsapp'),
    path('invoice/preview/', views.invoice_preview, name='invoice_preview'),
    path('invoice/<int:pk>/pay/', views.initialize_paystack_payment, name='initialize_payment'),
    path('invoice/<int:pk>/whatsapp-pay/', views.send_whatsapp_payment_link, name='whatsapp_payment_link'),
    path('payment/callback/', views.payment_callback, name='payment_callback'),
    
    # API Endpoints
    path('api/invoices/<int:pk>/create-paystack-checkout/', views.create_paystack_checkout_api, name='create_paystack_checkout'),
    path('api/paystack/webhook/', views.paystack_webhook, name='paystack_webhook'),
    path('api/statistics/', views.invoice_statistics_api, name='invoice_statistics_api'),
    path('api/bulk/send/', views.bulk_send_invoices, name='bulk_send_invoices'),
    path('api/bulk/update-status/', views.bulk_update_status, name='bulk_update_status'),
    
    # System
    path('health/', views.health_check, name='health_check'),
    
    # Client Management
    path('clients/', views.client_list, name='client_list'),
    path('clients/create/', views.client_create, name='client_create'),
    path('clients/<int:pk>/', views.client_detail, name='client_detail'),
    path('clients/<int:pk>/edit/', views.client_update, name='client_update'),
    path('clients/<int:pk>/delete/', views.client_delete, name='client_delete'),
    
    # Analytics & Reports
    path('analytics/', views.analytics_dashboard, name='analytics_dashboard'),
    path('export/invoices/', views.export_invoices, name='export_invoices'),
    path('export/payments/', views.export_payments, name='export_payments'),
    path('export/clients/', views.export_clients, name='export_clients'),
    
    # Support
    path('faq/', views.faq_page, name='faq'),
    path('support/', views.support_page, name='support'),
]
