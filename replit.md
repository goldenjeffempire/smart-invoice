# Smart Invoice - Django Application

## Overview
Smart Invoice is a Django-based web application for creating and managing invoices. The application includes PDF generation capabilities using xhtml2pdf, reportlab, and pyHanko for digital signatures.

## Project Information
- **Framework**: Django 5.2.7
- **Python Version**: 3.11
- **Database**: SQLite3 (development)
- **Key Features**: Invoice management, PDF generation, email functionality

## Current State
- Successfully configured for Replit environment
- Dependencies installed including Django, gunicorn, and PDF libraries
- Database migrations completed
- Static files collected
- Development server configured on port 5000

## Project Structure
- `smart_invoice/`: Django project configuration
  - `settings.py`: Main settings (configured for Replit with allowed hosts)
  - `urls.py`: URL routing
  - `wsgi.py`: WSGI configuration for deployment
- `invoices/`: Main application
  - `models.py`: Database models
  - `views.py`: Application views
  - `templates/`: HTML templates
  - `static/`: Static files (CSS, JS, images)
- `staticfiles/`: Collected static files for production
- `db.sqlite3`: SQLite database file
- `manage.py`: Django management script

## Configuration
- **DEBUG Mode**: Enabled for development (set via DJANGO_DEBUG env var)
- **Allowed Hosts**: Configured for Replit domains (.replit.dev, .replit.app) and Render (.onrender.com)
- **Static Files**: Using WhiteNoise for serving static files
- **Email Backend**: Console backend in development, SMTP in production

## Development
- Server runs on: `0.0.0.0:5000`
- Access via Replit's webview proxy

## Dependencies
Key packages include:
- Django 5.2.7
- gunicorn 23.0.0
- xhtml2pdf 0.2.17
- reportlab 4.4.4
- pyHanko 0.31.0
- django-crispy-forms 2.4
- whitenoise 6.11.0
- python-dotenv 1.1.1

## Environment Variables
- `DJANGO_SECRET_KEY`: Secret key for Django (auto-generated if not set)
- `DJANGO_DEBUG`: Enable/disable debug mode (default: True in dev)
- `DJANGO_ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS`: Email configuration
- `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`: Email credentials (optional)

## Recent Changes
- 2025-10-22: Initial Replit setup and configuration
  - Installed Python 3.11 and all dependencies
  - Configured Django settings for Replit proxy environment
  - Added comprehensive .gitignore for Python/Django
  - Set up development workflow on port 5000
  - Installed system dependencies (cairo, pkg-config) for PDF generation
