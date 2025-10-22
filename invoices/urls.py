from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('create/', views.create_invoice, name='create_invoice'),
    path('invoice/<int:pk>/', views.invoice_detail, name='invoice_detail'),
    path('invoice/<int:pk>/pdf/', views.invoice_pdf, name='invoice_pdf'),
    path('invoice/<int:pk>/send/', views.send_invoice_email, name='send_invoice_email'),
    path('invoice/<int:pk>/send-whatsapp/', views.send_invoice_whatsapp, name='send_invoice_whatsapp'),
    path('invoice/preview/', views.invoice_preview, name='invoice_preview'),
]
