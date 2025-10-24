# Smart Invoice 📄✨

**Production-ready** invoicing platform built with Django featuring **Paystack payments** and **WhatsApp Pay Now** integration. Created for modern businesses by [Jeffery Onome](https://onome-portfolio-ten.vercel.app).

![Smart Invoice Platform](https://img.shields.io/badge/Django-5.2.7-green) ![Python](https://img.shields.io/badge/Python-3.11-blue) ![TailwindCSS](https://img.shields.io/badge/TailwindCSS-4.1-cyan) ![Paystack](https://img.shields.io/badge/Paystack-Integrated-blue) ![Tests](https://img.shields.io/badge/Tests-Passing-success)

---

## 🚀 Features

### 💳 **Payment Processing** (NEW!)
- **Paystack Checkout API** - Create payment links via `POST /api/invoices/<id>/create-paystack-checkout/`
- **WhatsApp Pay Now** - One-click button that opens WhatsApp with payment link
- **Webhook Security** - Signature verification with idempotency handling
- **Real-time Updates** - Automatic invoice status updates via webhooks
- **Payment Tracking** - Complete transaction history with detailed logs

### 📄 **Invoice Management**
- Create & edit professional invoices with real-time preview
- Multi-currency support (USD, EUR, GBP, NGN, CAD, AUD)
- PDF generation with branded templates
- Status tracking (Draft, Sent, Paid, Overdue, Cancelled)
- Flexible payment terms (Immediate, Net 15/30/60/90)

### 👥 **Client Management**
- Customer database with comprehensive records
- Invoice history per client
- Revenue analytics by client
- Automated client-invoice linking

### 📊 **Analytics & Reporting**
- Revenue dashboard with trend visualization
- Client analytics and top clients
- Payment statistics and success rates
- CSV exports for invoices, payments, and clients

### 📧 **Communication**
- Email invoices with PDF attachments
- WhatsApp integration (Twilio-powered)
- Automated payment reminders

### 🎨 **Modern UI/UX**
- Glassmorphism design with purple/pink gradients
- Fully responsive (mobile, tablet, desktop)
- Advanced animations and micro-interactions
- Dark theme optimized

---

## 🛠️ Tech Stack

| Category | Technology |
|----------|-----------|
| **Backend** | Django 5.2.7, Python 3.11 |
| **Database** | PostgreSQL (prod), SQLite (dev) |
| **Payments** | Paystack API |
| **Styling** | TailwindCSS 4.1 |
| **PDF** | xhtml2pdf, reportlab, pycairo |
| **WhatsApp** | Twilio API |
| **Static Files** | WhiteNoise |
| **Testing** | pytest, pytest-django |
| **CI/CD** | GitHub Actions |
| **Containers** | Docker, docker-compose |

---

## 📦 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+ & npm
- PostgreSQL (production) or SQLite (development)

### Installation

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd smart-invoice

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Install Node dependencies (for TailwindCSS)
npm install

# 4. Set up environment variables
cp .env.example .env
# Edit .env with your configuration (see below)

# 5. Run migrations
python manage.py migrate

# 6. Create superuser
python manage.py createsuperuser

# 7. Collect static files
python manage.py collectstatic --noinput

# 8. Build TailwindCSS
npm run build:css

# 9. Run development server
python manage.py runserver 0.0.0.0:5000
```

Visit `http://localhost:5000` 🎉

---

## 🔑 Environment Variables

Create a `.env` file based on `.env.example`:

```env
# Django Configuration
DJANGO_SECRET_KEY=your-secret-key-here-change-in-production
DJANGO_ENV=development
DEBUG=False

# Database (leave empty for SQLite in dev)
DATABASE_URL=postgres://user:password@localhost:5432/smart_invoice

# Site Configuration
SITE_URL=https://yourdomain.com
DJANGO_ALLOWED_HOSTS=.yourdomain.com,.vercel.app
CSRF_TRUSTED_ORIGINS=https://yourdomain.com

# ⚡ Paystack Payment Gateway (REQUIRED)
PAYSTACK_PUBLIC_KEY=pk_test_xxxxxxxxxxxxx
PAYSTACK_SECRET_KEY=sk_test_xxxxxxxxxxxxx
PAYSTACK_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxx

# 📱 WhatsApp Configuration (REQUIRED for Pay Now button)
WHATSAPP_NUMBER=2348xxxxxxxxx

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Twilio (Optional - for WhatsApp invoice delivery)
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxx
TWILIO_WHATSAPP_NUMBER=+14155238886
```

---

## 💳 Paystack + WhatsApp Setup

### 1. Get Paystack API Keys

1. Sign up at [paystack.com](https://paystack.com)
2. Navigate to **Settings → API Keys & Webhooks**
3. Copy your **Public Key** and **Secret Key**
4. Add them to your `.env` file

### 2. Configure Webhook

1. In Paystack Dashboard, go to **Settings → API Keys & Webhooks**
2. Click **Add Webhook Endpoint**
3. Enter your webhook URL: `https://yourdomain.com/api/paystack/webhook/`
4. Select events: `charge.success` and `charge.failed`
5. Copy the **Webhook Secret** to your `.env` as `PAYSTACK_WEBHOOK_SECRET`

### 3. WhatsApp Pay Now Setup

1. Add your WhatsApp number (with country code) to `.env`:
   ```env
   WHATSAPP_NUMBER=2348012345678
   ```

2. The **"Pay via WhatsApp"** button will:
   - Create Paystack checkout link via `POST /api/invoices/<id>/create-paystack-checkout/`
   - Open WhatsApp with pre-filled message containing payment link
   - Client clicks link → pays securely → invoice auto-updates to "Paid"

### 4. Test Mode

Use Paystack test keys for development:
- Test cards: `4084084084084081` (success), `5060666666666666666` (decline)
- Webhook signature verification works in test mode

---

## 🔗 API Endpoints

### Create Paystack Checkout
```http
POST /api/invoices/<id>/create-paystack-checkout/
```

**Response:**
```json
{
  "success": true,
  "checkout_url": "https://checkout.paystack.com/abc123",
  "reference": "INV-12345678-20251024",
  "invoice_id": "INV-A1B2C3D4",
  "amount": 1000.00,
  "currency": "NGN"
}
```

### Paystack Webhook
```http
POST /api/paystack/webhook/
X-Paystack-Signature: <signature>
```

Handles `charge.success` and `charge.failed` events with:
- ✅ HMAC-SHA512 signature verification
- ✅ Idempotency (duplicate events handled gracefully)
- ✅ Amount validation
- ✅ Automatic invoice status updates

---

## 🐳 Docker Deployment

### Using Docker Compose

```bash
# 1. Build and start services
docker-compose up -d

# 2. Run migrations
docker-compose exec web python manage.py migrate

# 3. Create superuser
docker-compose exec web python manage.py createsuperuser

# 4. View logs
docker-compose logs -f web
```

Access at `http://localhost:5000`

### Production Dockerfile

Multi-stage build included for optimized production deployment:
- Python 3.11-slim base
- Non-root user for security
- Health checks configured
- Gunicorn with 4 workers

---

## ☁️ Deployment Guides

### Deploy to Vercel (Recommended for Django)

1. Install Vercel CLI:
   ```bash
   npm install -g vercel
   ```

2. Deploy:
   ```bash
   vercel
   ```

3. Set environment variables in Vercel dashboard

4. Configure database (use Vercel Postgres or external PostgreSQL)

### Deploy to Render

1. Create `render.yaml` (already included)

2. Connect your GitHub repo to Render

3. Set environment variables:
   - `DJANGO_SECRET_KEY`
   - `DATABASE_URL` (Render provides this)
   - All Paystack and WhatsApp variables

4. Deploy! Render auto-runs `build.sh`

### Deploy to Replit (Current Platform)

Already configured! Just:
1. Set Secrets in Replit Secrets tab
2. Click **Run** button
3. Configure custom domain in Deployment tab

---

## 🧪 Testing

### Run Tests

```bash
# Install test dependencies
pip install pytest pytest-django pytest-cov

# Run all tests
pytest

# Run with coverage
pytest --cov=invoices --cov-report=html

# Run specific test file
pytest invoices/tests/test_webhooks.py -v
```

### Test Coverage

- Payment service initialization and verification
- Webhook signature validation and idempotency
- API endpoint authentication and error handling
- Payment success/failure processing

---

## 🚀 Production Checklist

- [ ] Set strong `DJANGO_SECRET_KEY`
- [ ] Set `DEBUG=False`
- [ ] Configure production `DATABASE_URL`
- [ ] Set `DJANGO_ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS`
- [ ] Use Paystack **live** keys (not test keys)
- [ ] Configure Paystack webhook URL
- [ ] Set up email SMTP credentials
- [ ] Configure WhatsApp number
- [ ] Run `python manage.py check --deploy`
- [ ] Set up SSL/HTTPS
- [ ] Configure backup strategy for database
- [ ] Set up monitoring (Sentry recommended)

---

## 📁 Project Structure

```
smart-invoice/
├── invoices/                 # Main Django app
│   ├── models.py            # Invoice, Client, Payment models
│   ├── views.py             # All view logic including API endpoints
│   ├── payment_service.py   # Paystack integration service
│   ├── analytics.py         # Analytics and reporting
│   ├── forms.py             # Django forms
│   ├── urls.py              # URL routing
│   ├── templates/           # HTML templates
│   └── tests/               # Comprehensive test suite
├── smart_invoice/           # Project settings
│   └── settings/            # Split settings (dev/prod)
├── staticfiles/             # Collected static files
├── .env.example             # Environment variables template
├── Dockerfile               # Multi-stage production build
├── docker-compose.yml       # Local Docker setup
├── requirements.txt         # Python dependencies
├── pytest.ini               # Test configuration
└── README.md                # This file
```

---

## 🔧 Development Workflow

### TailwindCSS Watch Mode

```bash
npm run watch:css  # Auto-rebuild CSS on changes
```

### Database Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Create Test Data

```bash
python manage.py shell
>>> from invoices.tests.factories import create_test_data
>>> create_test_data()
```

---

## 🐛 Troubleshooting

### Paystack Webhook Not Working

1. Check webhook URL is publicly accessible (use ngrok for local testing)
2. Verify `PAYSTACK_WEBHOOK_SECRET` matches Paystack dashboard
3. Check webhook logs: `docker-compose logs -f web | grep webhook`
4. Test signature manually:
   ```python
   import hmac, hashlib
   signature = hmac.new(secret.encode(), payload.encode(), hashlib.sha512).hexdigest()
   ```

### WhatsApp Pay Now Button Not Appearing

1. Ensure `WHATSAPP_NUMBER` is set in environment
2. Check invoice has valid client phone number
3. Verify Paystack keys are configured

### Static Files Not Loading

```bash
python manage.py collectstatic --clear --noinput
npm run build:css
```

### Database Migrations Failing

```bash
# Reset migrations (⚠️ development only!)
python manage.py migrate --fake-initial
```

---

## 📝 Changelog

### v2.0.0 (October 2025)
- ✨ **NEW**: Paystack checkout API endpoint (`POST /api/invoices/<id>/create-paystack-checkout/`)
- ✨ **NEW**: WhatsApp Pay Now button integration
- 🔒 **SECURITY**: Webhook signature verification with dedicated `PAYSTACK_WEBHOOK_SECRET`
- 🔒 **SECURITY**: Idempotent webhook handling prevents duplicate payments
- ✅ **TESTS**: Comprehensive test suite (payment service, webhooks, API)
- 🐳 **DOCKER**: Multi-stage Dockerfile and docker-compose setup
- 🚀 **CI/CD**: GitHub Actions workflow for automated testing
- 📝 **DOCS**: Complete README with deployment guides
- ♿ **SEO**: JSON-LD schema for FAQ page

### v1.0.0 (October 2025)
- Initial release with core invoicing features
- Paystack payment integration
- Client management system
- Analytics dashboard

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'feat: add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

**Commit Message Convention:**
- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation updates
- `test:` Test additions/updates
- `chore:` Maintenance tasks

---

## 📄 License

This project is licensed under the MIT License.

---

## 👨‍💻 Author

**Built by Jeffery Onome**

- Portfolio: [onome-portfolio-ten.vercel.app](https://onome-portfolio-ten.vercel.app)
- Expertise: Full-Stack Software Engineer & AI/ML Specialist

---

## 🙏 Acknowledgments

- Django framework and community
- Paystack for secure payment processing
- Twilio for WhatsApp integration
- TailwindCSS for beautiful UI
- All open-source contributors

---

## 📞 Support

- **FAQ**: Visit `/faq/` page
- **Support Form**: `/support/` page
- **Issues**: Open GitHub issue
- **Email**: Contact via support form

---

**⭐ Star this repo if you find it useful!**

Built with ❤️ using Django, Paystack, and modern web technologies.
