# Smart Invoice

## Overview
Smart Invoice is a professional Django-based invoice management system designed for freelancers, startups, and growing teams. The application allows users to create, manage, and send professional invoices via email or WhatsApp.

## Current State
The application is fully functional and running on Replit. The development server is configured and the database has been migrated successfully.

## Recent Changes (October 22, 2025)
- Imported project from GitHub to Replit
- Installed Python 3.11 and all required dependencies including Django 5.2.7
- Installed system dependencies (cairo, pkg-config) for PDF generation
- Updated Django settings for Replit environment:
  - Added wildcard to ALLOWED_HOSTS for Replit domains
  - Set DEBUG=True for development
  - Added X_FRAME_OPTIONS and CSRF_TRUSTED_ORIGINS for Replit iframe
  - Added Twilio configuration settings for WhatsApp functionality
- Ran database migrations
- Collected static files with WhiteNoise
- Set up development server workflow on port 5000

## Project Architecture

### Tech Stack
- **Backend**: Django 5.2.7 (Python web framework)
- **Database**: SQLite (for development)
- **PDF Generation**: xhtml2pdf, reportlab, pycairo
- **Styling**: TailwindCSS (via CDN in development)
- **Static Files**: WhiteNoise for static file serving
- **Email**: Django SMTP backend (console backend for development)
- **WhatsApp**: Twilio API integration

### Project Structure
```
smart_invoice/
├── invoices/              # Main app for invoice management
│   ├── models.py         # Invoice data model
│   ├── views.py          # Business logic and views
│   ├── forms.py          # Invoice forms
│   ├── urls.py           # App URL routing
│   ├── templates/        # HTML templates
│   └── static/           # Static assets (images, CSS)
├── smart_invoice/        # Project configuration
│   ├── settings.py       # Django settings
│   ├── urls.py           # Root URL configuration
│   └── wsgi.py           # WSGI configuration
├── staticfiles/          # Collected static files
├── db.sqlite3            # SQLite database
├── manage.py             # Django management script
└── requirements.txt      # Python dependencies
```

### Key Features
1. **Invoice Management**: Create, update, and track invoices with various statuses (draft, sent, paid, overdue, cancelled)
2. **PDF Generation**: Generate professional PDF invoices with custom branding
3. **Email Integration**: Send invoices via email with PDF attachments
4. **WhatsApp Integration**: Send invoices via WhatsApp using Twilio API
5. **Multi-currency Support**: USD, EUR, GBP, NGN, CAD, AUD
6. **Payment Terms**: Flexible payment terms (immediate, net 15/30/60/90)
7. **Professional Templates**: Modern, responsive invoice templates

### Database Schema
- **Invoice Model**: Contains all invoice details including:
  - Business information (name, email, address, phone, logo)
  - Client information (name, email, phone, address)
  - Line items (description, quantity, unit price)
  - Financial calculations (subtotal, tax, discount, total)
  - Status tracking and payment terms
  - Dates (issue, due, paid)

## Environment Variables
The following environment variables can be configured:

### Django Settings
- `DJANGO_SECRET_KEY`: Secret key for Django (auto-generated if not set)
- `DJANGO_DEBUG`: Set to 'True' for debug mode (default: 'True')
- `DJANGO_ALLOWED_HOSTS`: Comma-separated list of allowed hosts

### Email Configuration (Optional)
- `EMAIL_HOST`: SMTP server (default: smtp.gmail.com)
- `EMAIL_PORT`: SMTP port (default: 587)
- `EMAIL_USE_TLS`: Use TLS (default: True)
- `EMAIL_HOST_USER`: SMTP username
- `EMAIL_HOST_PASSWORD`: SMTP password

### Twilio/WhatsApp Configuration (Optional)
- `TWILIO_ACCOUNT_SID`: Twilio account SID
- `TWILIO_AUTH_TOKEN`: Twilio auth token
- `TWILIO_WHATSAPP_NUMBER`: Twilio WhatsApp number

## Running the Application

### Development
The development server runs automatically on port 5000:
```bash
python manage.py runserver 0.0.0.0:5000
```

### Production
For production deployment, use Gunicorn (already in requirements.txt):
```bash
gunicorn smart_invoice.wsgi:application --bind 0.0.0.0:5000
```

## Important Notes
- The application uses SQLite for development, which is suitable for small-scale use
- TailwindCSS is loaded via CDN in development (should be compiled for production)
- Email sending defaults to console backend in DEBUG mode
- WhatsApp functionality requires Twilio credentials to be configured
- Static files are served by WhiteNoise in production
