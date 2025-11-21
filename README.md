# Smart Invoice - Production-Ready Django SaaS Platform

Smart, Simple Invoicing for modern businesses. Create professional invoices in minutes, send via email or WhatsApp, and get paid faster.

## Features

### 🎨 Frontend Pages
- **Pixel-perfect responsive landing page** with hero section, stats (10,000 users, 99% satisfaction, lightning fast), features grid, testimonials with avatars/ratings, 3-step workflow, and professional footer
- **Complete navigation** including Features, FAQ, Support, Dashboard, Login, and Sign Up pages
- **Smooth animations** and gradient effects for modern UI/UX
- **Mobile-first design** that works perfectly on all devices

### 🧾 Invoice System
- **User accounts** with signup, login, logout, and password reset functionality
- **Multi-step invoice creation** with:
  - Business information (name, email, phone, address)
  - Client information (name, email, phone, address)
  - Dynamic line items with add/remove functionality
  - Auto-generated invoice IDs (e.g., INV123456)
  - Auto-populated invoice date
  - Subtotal, tax, and total calculations
- **Multi-currency support**: USD, EUR, GBP, NGN, CAD, AUD
- **Custom branding**: Upload logo, set brand color, add brand name
- **Bank transfer details**: Account name, account number, bank name on every invoice
- **Invoice persistence** per user with full CRUD operations
- **Invoice dashboard** with filtering (all/paid/unpaid)

### 📄 PDF Generation
- **High-fidelity PDF generation** using WeasyPrint
- **Branded design** with custom colors and logo
- **Professional layout** matching invoice design standards
- **Footer credit**: "Built by Jeffery Onome — https://onome-portfolio-ten.vercel.app/"
- **Download functionality** for all invoices

### 📬 Communication
- **SMTP email sending** with PDF attachment
- **WhatsApp share link** with preloaded invoice preview
- **Customizable email** templates

### 📊 Smart Analytics
- **Invoice creation count** tracking
- **Paid/Unpaid status** monitoring
- **Total revenue** calculation
- **Unique clients** count
- **Dashboard widgets** with real-time statistics

### ☁️ Cloud Backend
- **Secure Django backend** with authentication
- **PostgreSQL-ready** configuration
- **Environment variables** for production secrets
- **Production-ready settings** with DEBUG toggle

### 🔐 Admin Panel
- **Django admin** with full control over:
  - Invoices and line items
  - Users and permissions
  - Analytics and reporting
  - Branding settings

## Technology Stack

### Backend
- **Django 5.0.1** - Modern Python web framework
- **PostgreSQL** - Production database (SQLite for development)
- **Gunicorn** - WSGI HTTP server for production
- **WeasyPrint** - High-quality PDF generation
- **Pillow** - Image processing for logos

### Frontend
- **HTML5/CSS3/JavaScript** - Core web technologies
- **Tailwind CSS** - Utility-first CSS framework (CDN)
- **Responsive design** - Mobile-first approach

### Production
- **WhiteNoise** - Static file serving
- **django-environ** - Environment variable management
- **SMTP** - Email delivery

## Installation

### Prerequisites
- Python 3.11+
- PostgreSQL (for production)
- System dependencies for WeasyPrint:
  - libpango-1.0-0
  - libpangocairo-1.0-0
  - libgdk-pixbuf2.0-0
  - shared-mime-info

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd smart-invoice
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

4. **Run migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create a superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver 0.0.0.0:5000
   ```

7. **Access the application**
   - Homepage: http://localhost:5000/
   - Admin: http://localhost:5000/admin/

## Render Deployment

### Prerequisites
- Render account
- PostgreSQL database on Render

### Deployment Steps

1. **Create a new Web Service on Render**

2. **Configure build settings**
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn smart_invoice.wsgi:application --bind 0.0.0.0:$PORT`

3. **Set environment variables**
   ```
   DEBUG=False
   SECRET_KEY=<your-secure-secret-key>
   DATABASE_URL=<your-postgresql-database-url>
   ALLOWED_HOSTS=<your-render-domain>.onrender.com
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=<your-email>
   EMAIL_HOST_PASSWORD=<your-email-password>
   DEFAULT_FROM_EMAIL=<your-sender-email>
   ```

4. **Deploy**
   - Push to your connected Git repository
   - Render will automatically build and deploy

### Post-Deployment

1. **Create superuser** (via Render Shell)
   ```bash
   python manage.py createsuperuser
   ```

2. **Collect static files** (if not done in build)
   ```bash
   python manage.py collectstatic --noinput
   ```

## Configuration

### Email Setup
For email functionality, configure SMTP settings in your environment:

**Gmail Setup**:
1. Enable 2-Factor Authentication
2. Generate an App Password
3. Use the App Password in `EMAIL_HOST_PASSWORD`

**Other SMTP Providers**:
- Update `EMAIL_HOST` and `EMAIL_PORT` accordingly
- Ensure `EMAIL_USE_TLS` is set correctly

### Database
- **Development**: SQLite (default)
- **Production**: PostgreSQL (set via `DATABASE_URL`)

## Usage

### Creating an Invoice

1. **Sign up** for an account
2. **Log in** to your dashboard
3. Click **"Create New Invoice"**
4. Fill in:
   - Business information
   - Client information
   - Line items (add multiple)
   - Tax rate
   - Branding (optional)
   - Bank details (optional)
5. Click **"Create Invoice"**

### Managing Invoices

- **View**: Click on any invoice from the dashboard
- **Edit**: Click "Edit" on invoice detail page
- **Delete**: Click "Delete" on invoice detail page
- **Download PDF**: Click "Download PDF" button
- **Send Email**: Click "Send Email" and enter recipient
- **Share WhatsApp**: Click "WhatsApp" to share via messaging

### Tracking Payments

1. Open invoice detail page
2. Use status dropdown to mark as "Paid" or "Unpaid"
3. View analytics on dashboard

## Project Structure

```
smart-invoice/
├── smart_invoice/          # Django project settings
│   ├── settings.py        # Main configuration
│   ├── urls.py            # URL routing
│   └── wsgi.py            # WSGI configuration
├── invoices/              # Main application
│   ├── models.py          # Database models
│   ├── views.py           # View logic
│   ├── forms.py           # Form definitions
│   ├── admin.py           # Admin configuration
│   └── urls.py            # App URL routing
├── templates/             # HTML templates
│   ├── base.html          # Base template
│   ├── home.html          # Landing page
│   ├── registration/      # Auth templates
│   ├── invoices/          # Invoice templates
│   ├── pages/             # Static pages
│   └── includes/          # Reusable components
├── static/                # Static files (CSS, JS, images)
├── media/                 # User uploads (logos, invoices)
├── requirements.txt       # Python dependencies
├── build.sh              # Render build script
├── .env.example          # Environment variables template
└── README.md             # This file
```

## Security

- **CSRF Protection**: Enabled on all forms
- **Password Hashing**: Django's built-in PBKDF2
- **SQL Injection**: Protected by Django ORM
- **XSS Protection**: Auto-escaping in templates
- **HTTPS**: Enforced in production
- **Secure Cookies**: Enabled in production

## Credits

**Built by Jeffery Onome**
- Portfolio: https://onome-portfolio-ten.vercel.app/
- Email: jeffemuodafe124@gmail.com

## License

All rights reserved.

## Support

- **Email**: support@smartinvoice.com
- **FAQ**: Visit /faq/ on the website
- **Support Page**: Visit /support/ on the website
