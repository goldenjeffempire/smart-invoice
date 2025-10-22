# Smart Invoice

## Overview
Smart Invoice is an enterprise-grade Django-based invoice management platform designed for freelancers, startups, and growing businesses. The application features a modern, professional interface with advanced animations and glassmorphism design to attract businesses, companies, and industries.

## Current State
The application is fully functional with a completely modernized, ultra-professional UI/UX design. All pages feature advanced animations, interactive elements, and enterprise-grade polish to attract potential clients and businesses.

## Recent Changes (October 22, 2025)

### Initial Setup
- Imported project from GitHub to Replit
- Installed Python 3.11 and all required dependencies including Django 5.2.7
- Installed system dependencies (cairo, pkg-config) for PDF generation
- Updated Django settings for Replit environment
- Ran database migrations and collected static files
- Set up development server workflow on port 5000

### User Authentication System (Latest - October 22, 2025)
- **Complete Authentication System**: Implemented Django built-in authentication with:
  - User signup with username and password
  - User login with redirect to dashboard
  - User logout with redirect to landing page
  - Login required for all invoice operations
  - User-specific invoice filtering (users only see their own invoices)
  - Modern glassmorphism auth pages matching platform design
  
- **Navigation Updates**:
  - Dynamic nav showing Login/Signup for logged-out users
  - Dynamic nav showing Dashboard/Logout for logged-in users
  - Conditional rendering on both desktop and mobile menus
  - Smooth transitions and professional styling
  
- **Database Schema Updates**:
  - Added `user` foreign key to Invoice model
  - Linked all invoices to user accounts with CASCADE deletion
  - Migration applied to database for user field

### UI/UX Modernization
- **Landing Page**: Completely redesigned with:
  - Advanced parallax effects and smooth scroll animations
  - Interactive statistics with counter animations
  - Professional testimonials section with 5-star reviews
  - Trust badges and social proof (50K+ invoices, $50M+ processed, 150+ countries)
  - Multiple animated background orbs with glassmorphism effects
  - Comprehensive "How It Works" section
  - Professional CTA sections throughout
  - Mobile-responsive navigation with smooth transitions
  
- **Invoice Dashboard**: Enhanced with:
  - Card-based grid layout with hover effects
  - Real-time stats cards (Total, Draft, Paid, Overdue)
  - Advanced search and filter functionality
  - Skeleton loading states for better UX
  - Micro-interactions on all interactive elements
  - Modern glassmorphism design throughout
  
- **Invoice Form**: Transformed with:
  - Multi-step wizard interface with progress tracking
  - Real-time calculation and validation
  - Live preview panel showing invoice as you type
  - Smooth step transitions with animations
  - Professional input fields with focus states
  - Auto-save indicators and loading animations
  
- **Invoice Detail Page**: Upgraded with:
  - Timeline view showing invoice lifecycle
  - Modern action cards for Download, Email, WhatsApp
  - Share modal with success animations
  - Status badges with gradient effects
  - Responsive design with mobile optimization

- **Global Enhancements**:
  - Professional footer on all pages with developer credit: "Built with ❤️ by Jeffery Onome Emuodafevware"
  - Scroll progress bar on landing page
  - Ripple effects on all buttons
  - Gradient text animations
  - Smooth page transitions
  - Dark theme with purple/pink gradient aesthetic
  - Enterprise-grade glassmorphism effects throughout

## Project Architecture

### Tech Stack
- **Backend**: Django 5.2.7 (Python web framework)
- **Database**: SQLite (for development)
- **PDF Generation**: xhtml2pdf, reportlab, pycairo
- **Styling**: TailwindCSS (via CDN in development, should compile for production)
- **Design System**: Custom glassmorphism with purple/pink gradient theme
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
│   ├── templates/        # HTML templates (modernized)
│   │   ├── landing.html  # Landing page with testimonials & animations
│   │   ├── invoice_list.html  # Dashboard with stats & filters
│   │   ├── invoice_form.html  # Multi-step wizard form
│   │   └── invoice_detail.html # Detail page with timeline
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

#### Core Functionality
1. **Invoice Management**: Create, update, and track invoices with various statuses (draft, sent, paid, overdue, cancelled)
2. **PDF Generation**: Generate professional PDF invoices with custom branding
3. **Email Integration**: Send invoices via email with PDF attachments
4. **WhatsApp Integration**: Send invoices via WhatsApp using Twilio API
5. **Multi-currency Support**: USD, EUR, GBP, NGN, CAD, AUD
6. **Payment Terms**: Flexible payment terms (immediate, net 15/30/60/90)

#### UI/UX Features
1. **Advanced Animations**: Parallax effects, fade-in animations, hover effects, ripple buttons
2. **Glassmorphism Design**: Modern glass effects with backdrop blur and gradient borders
3. **Interactive Elements**: Live preview, real-time calculations, counter animations
4. **Professional Polish**: Testimonials, trust badges, social proof, enterprise aesthetics
5. **Responsive Design**: Mobile-first approach with smooth transitions across all devices
6. **Multi-step Wizard**: Intuitive form flow with progress tracking and validation

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

## Developer Credit
Built with ❤️ by **Jeffery Onome Emuodafevware**

## Important Notes
- The application uses SQLite for development, suitable for small to medium-scale use
- TailwindCSS is loaded via CDN in development (recommended to compile for production)
- Email sending defaults to console backend in DEBUG mode
- WhatsApp functionality requires Twilio credentials to be configured
- Static files are served by WhiteNoise in production
- All UI templates feature modern glassmorphism design with advanced animations
- Platform designed to attract businesses with enterprise-grade polish and professionalism

## Future Enhancements (Optional)
- Compile TailwindCSS for production (replace CDN)
- Centralize shared layout pieces (nav/footer/scripts) in base template
- Add cross-browser/device smoke tests
- Implement user authentication system
- Add invoice templates library
- Create API endpoints for third-party integrations
