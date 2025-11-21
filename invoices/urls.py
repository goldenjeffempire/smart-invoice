from django.urls import path
from . import views

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path("analytics/", views.analytics, name="analytics"),
    path("create/", views.create_invoice, name="create_invoice"),
    path("invoice/<int:invoice_id>/", views.invoice_detail, name="invoice_detail"),
    path("invoice/<int:invoice_id>/edit/", views.edit_invoice, name="edit_invoice"),
    path("invoice/<int:invoice_id>/delete/", views.delete_invoice, name="delete_invoice"),
    path(
        "invoice/<int:invoice_id>/status/",
        views.update_invoice_status,
        name="update_invoice_status",
    ),
    path("invoice/<int:invoice_id>/pdf/", views.generate_pdf, name="generate_pdf"),
    path("invoice/<int:invoice_id>/email/", views.send_invoice_email, name="send_invoice_email"),
    path("invoice/<int:invoice_id>/whatsapp/", views.whatsapp_share, name="whatsapp_share"),
]
