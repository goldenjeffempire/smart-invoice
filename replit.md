# Smart Invoice - Production-Ready Django SaaS Platform

## Overview

Smart Invoice is a full-stack Django SaaS application for creating, managing, and distributing professional invoices. The platform enables businesses to generate branded PDF invoices, send them via email or WhatsApp, track payment status, and analyze business performance through a comprehensive analytics dashboard.

**Core Value Proposition:** Simplify invoicing workflow from creation to payment tracking with multi-currency support, custom branding, and cloud-based invoice management.

**Technology Stack:**
- **Backend:** Django 5.2.8 (Python web framework)
- **Database:** PostgreSQL (production), SQLite (development)
- **Frontend:** Server-side rendered templates with Tailwind CSS
- **PDF Generation:** WeasyPrint
- **Image Processing:** Pillow
- **Deployment:** Replit Deployments (autoscale), Render (cloud platform)
- **Web Server:** Gunicorn with WhiteNoise for static files

## Recent Changes

**2025-11-20: Replit Environment Setup**
- Installed Python 3.11 and required system dependencies (pango, cairo, gdk-pixbuf, shared-mime-info) for WeasyPrint
- Installed all Python dependencies from requirements.txt
- Updated .gitignore to preserve Replit configuration files
- Ran database migrations to set up SQLite database for development
- Collected static files for WhiteNoise static file serving
- Configured Django dev server workflow on port 5000 with 0.0.0.0 host binding
- Configured autoscale deployment for production with Gunicorn

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Application Structure

**Monolithic Django Architecture:**
- Single Django project (`smart_invoice/`) containing core settings and routing
- One Django app (`invoices/`) handling all invoice-related functionality
- Template-based frontend with no separate frontend framework
- RESTful URL patterns for invoice operations

**Key Design Patterns:**
- **MTV (Model-Template-View):** Standard Django pattern with models defining data structure, views handling business logic, and templates rendering UI
- **Form-based data validation:** Django forms (`InvoiceForm`, `LineItemForm`, `SignUpForm`) for input validation
- **Class-based admin:** Custom admin interfaces with inline editing for related models

### Data Architecture

**Database Schema:**

**Invoice Model (Central Entity):**
- User relationship: Foreign key to Django's built-in User model
- Auto-generated invoice IDs using random string generation
- Multi-currency support via choices field (USD, EUR, GBP, NGN, CAD, AUD)
- Status tracking (paid/unpaid)
- Complete business and client contact information
- Branding fields (logo upload, brand color, brand name)
- Bank transfer details for payment instructions
- Timestamps for creation and updates

**LineItem Model:**
- Many-to-one relationship with Invoice
- Stores itemized billing details (description, quantity, unit_price)
- Auto-calculated totals

**Design Decisions:**
- **Inline editing:** LineItems managed through Django admin inlines for seamless UX
- **File uploads:** Media files (logos) stored in `logos/` directory
- **Soft delete:** No soft delete implemented; deletion is permanent
- **Audit trail:** Created/updated timestamps on invoices

### Authentication & Authorization

**Built-in Django Authentication:**
- Username/password authentication
- Email-based password reset flow
- Session-based authentication (no JWT/token system)
- Login-required decorators protect invoice operations
- User isolation: Users can only access their own invoices via `user` foreign key filtering

**Design Rationale:**
- Chose Django's built-in auth over custom solution for security and maintenance
- Session-based auth sufficient for server-rendered application
- Password reset leverages Django's email backend

### Frontend Architecture

**Server-Side Rendering:**
- Django template engine with template inheritance
- Base template (`base.html`) provides consistent layout/navigation
- Component-like includes (`includes/navbar.html`, `includes/footer.html`)
- Tailwind CSS via CDN for styling
- Custom CSS animations (`static/css/animations.css`)
- Vanilla JavaScript for interactions (`static/js/interactions.js`, `static/js/ux-enhancements.js`)

**Key Features:**
- Responsive design (mobile-first approach)
- Toast notification system (JavaScript class)
- Intersection Observer for scroll animations
- Counter animations for statistics
- Form validation client-side and server-side

**Design Rationale:**
- Server-side rendering chosen over SPA for SEO, simplicity, and faster initial page load
- Tailwind CDN enables rapid styling without build process
- Progressive enhancement: Core functionality works without JavaScript

### PDF Generation

**WeasyPrint Integration:**
- HTML-to-PDF conversion using custom template (`invoice_pdf.html`)
- Dynamic styling with invoice brand colors
- Embedded logo support
- Footer attribution: "Built by Jeffery Onome — https://onome-portfolio-ten.vercel.app/"

**Generation Flow:**
1. View renders HTML template with invoice data
2. WeasyPrint converts HTML/CSS to PDF
3. PDF returned as HTTP response with appropriate headers

**Design Decision:**
- WeasyPrint chosen over alternatives (ReportLab, pdfkit) for HTML/CSS compatibility and easier template maintenance

### Communication Features

**Email Integration:**
- Django's email backend (SMTP)
- PDF attachment functionality
- Configurable via environment variables for SMTP settings
- Uses `EmailMessage` class for attachments

**WhatsApp Sharing:**
- URL generation with pre-filled message
- Uses `wa.me` API with URL-encoded text
- Opens in new window/tab

**Design Rationale:**
- Email via SMTP provides maximum deliverability
- WhatsApp integration uses public API (no auth required)
- Both features designed as user-triggered actions (not automated)

### Analytics & Reporting

**Dashboard Metrics:**
- Total invoices count
- Paid/unpaid breakdown
- Revenue calculations (sum of paid invoice totals)
- Unique clients count
- Average invoice value

**Implementation:**
- Django ORM aggregations (`Sum`, `Count`, `Avg`)
- Database-level calculations for performance
- Real-time data (no caching layer)

**Design Decision:**
- Real-time calculations acceptable at current scale
- Future optimization: Add Redis caching for frequently accessed metrics

### Static Files & Media

**WhiteNoise Middleware:**
- Serves static files directly from Django in production
- No separate CDN required for static assets
- Efficient gzip compression and caching headers

**File Structure:**
- `static/`: CSS, JavaScript, images
- `media/logos/`: User-uploaded logo files
- `templates/`: Django templates organized by function

**Design Rationale:**
- WhiteNoise eliminates need for separate static file server
- Keeps deployment simple and cost-effective
- Sufficient for current traffic levels

### Environment Configuration

**django-environ Integration:**
- Environment variables for sensitive data (SECRET_KEY, DATABASE_URL)
- Different settings for development vs. production
- `.env` file for local development
- Render dashboard for production environment variables

**Critical Variables:**
- `DEBUG`: Boolean flag for development mode
- `SECRET_KEY`: Django cryptographic signing
- `DATABASE_URL`: PostgreSQL connection string
- `ALLOWED_HOSTS`: Comma-separated domain list
- `CSRF_TRUSTED_ORIGINS`: Trusted domains for CSRF

**Design Decision:**
- 12-factor app methodology for configuration management
- Fail-fast if SECRET_KEY not set in production
- Permissive defaults for development, strict for production

### Deployment Architecture

**Render Platform:**
- Single web service running Gunicorn
- Separate PostgreSQL database service
- Build script (`build.sh`) handles migrations and static collection
- Auto-deploy on git push

**Gunicorn Configuration:**
- 4 worker processes
- 120-second timeout for PDF generation
- Binds to dynamic PORT environment variable

**Design Rationale:**
- Render chosen for simplicity and free tier availability
- Gunicorn provides production-grade WSGI server
- Worker count (4) balances concurrency and memory usage

## External Dependencies

### Third-Party Services

**Email (SMTP):**
- **Purpose:** Send invoices via email with PDF attachments
- **Provider:** Configurable (Gmail recommended in docs)
- **Configuration:** SMTP host, port, username, password via environment variables
- **Integration Point:** Django's `EmailMessage` class

**WhatsApp Business API:**
- **Purpose:** Share invoices via messaging app
- **Implementation:** Public `wa.me` URL scheme (no API key required)
- **Limitation:** Opens WhatsApp client; doesn't send automatically

### Database

**PostgreSQL (Production):**
- **Purpose:** Persistent data storage for production
- **Provider:** Render Managed PostgreSQL
- **Connection:** DATABASE_URL environment variable
- **Features Used:** Standard SQL features, no PostgreSQL-specific extensions

**SQLite (Development):**
- **Purpose:** Local development database
- **Automatic:** Default Django configuration

**Migration Strategy:**
- Django ORM migrations manage schema changes
- Version-controlled migration files in `invoices/migrations/`

### Python Packages

**Core Dependencies:**
- **Django 5.0.1:** Web framework
- **psycopg2-binary 2.9.9:** PostgreSQL adapter
- **gunicorn 21.2.0:** WSGI HTTP server
- **WeasyPrint 60.2:** PDF generation
- **Pillow 10.2.0:** Image processing for logos
- **django-environ 0.11.2:** Environment variable management
- **whitenoise 6.6.0:** Static file serving

**Rationale for Key Choices:**
- **psycopg2-binary:** Pre-compiled for easier deployment (no C dependencies to build)
- **WeasyPrint:** Best HTML-to-PDF for Django templates
- **WhiteNoise:** Industry standard for static files in Django

### CDN Resources

**Tailwind CSS:**
- **Source:** `https://cdn.tailwindcss.com`
- **Purpose:** Utility-first CSS framework
- **Rationale:** No build process required; rapid prototyping

**Google Fonts:**
- **Source:** `https://fonts.googleapis.com`
- **Font:** Inter (weights 300-900)
- **Purpose:** Modern typography

### Future Integration Points

**Noted in UI as "Coming Soon":**
- Invoice templates library
- API access for programmatic invoice creation
- Additional payment gateway integrations

**Recommended Additions:**
- **Redis:** For caching analytics and session storage
- **Celery:** For async email sending and PDF generation
- **AWS S3/Cloudinary:** For scalable media file storage
- **Stripe/PayPal:** For online payment processing