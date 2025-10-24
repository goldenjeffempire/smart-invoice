# 🚀 Smart Invoice - Production Deployment Guide

Complete step-by-step guide for deploying Smart Invoice to production on Render, Replit, or custom servers.

---

## 📋 Table of Contents

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Render Deployment (Recommended)](#render-deployment)
3. [Replit Deployment](#replit-deployment)
4. [Docker Deployment](#docker-deployment)
5. [Custom Server Deployment](#custom-server-deployment)
6. [Post-Deployment Steps](#post-deployment-steps)
7. [Monitoring & Maintenance](#monitoring--maintenance)
8. [Troubleshooting](#troubleshooting)

---

## ✅ Pre-Deployment Checklist

Before deploying to production, complete these essential steps:

### 1. Security Configuration

```bash
# Generate a strong secret key
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'

# Save this key securely - you'll need it for environment variables
```

- [ ] Generate unique `DJANGO_SECRET_KEY`
- [ ] Set `DEBUG=False`
- [ ] Configure `DJANGO_ALLOWED_HOSTS` with your domain
- [ ] Set `CSRF_TRUSTED_ORIGINS` with `https://your-domain.com`
- [ ] Enable SSL/HTTPS settings
- [ ] Review all environment variables in `.env.example`

### 2. Database Setup

- [ ] Set up PostgreSQL database (required for production)
- [ ] Have `DATABASE_URL` connection string ready
- [ ] Plan backup strategy
- [ ] Test database migrations locally

### 3. External Services

- [ ] **Paystack:** Get production API keys from [dashboard.paystack.com](https://dashboard.paystack.com)
- [ ] **Email:** Configure SMTP credentials (Gmail, SendGrid, etc.)
- [ ] **WhatsApp:** Get business phone number for Pay Now feature
- [ ] **Twilio (Optional):** Get credentials for WhatsApp invoice delivery

### 4. Code Preparation

```bash
# Run production checks
python manage.py check --deploy --settings=smart_invoice.settings.prod

# Test static files collection
python manage.py collectstatic --noinput --settings=smart_invoice.settings.prod

# Verify TailwindCSS build
npm run build:css
```

- [ ] All Django system checks pass (`0 issues`)
- [ ] Static files collect successfully
- [ ] TailwindCSS compiles without errors
- [ ] Git repository is clean and pushed

---

## 🌐 Render Deployment

### Step 1: Create Render Account

1. Sign up at [render.com](https://render.com)
2. Connect your GitHub account
3. Install Render GitHub App on your repository

### Step 2: Create PostgreSQL Database

1. Go to Render Dashboard → **New** → **PostgreSQL**
2. Configure database:
   - **Name:** `smart-invoice-db`
   - **Database:** `smartinvoice`
   - **Region:** Choose closest to your users
   - **Plan:** Starter ($7/month) or Free
3. Click **Create Database**
4. Copy the **Internal Database URL** (starts with `postgresql://`)

### Step 3: Create Web Service

1. Go to Render Dashboard → **New** → **Web Service**
2. Select your GitHub repository
3. Configure service:

#### Basic Settings
```
Name: smart-invoice
Region: Same as database
Branch: main
Runtime: Python 3
```

#### Build & Deploy Settings
```
Build Command: ./build.sh
Start Command: gunicorn smart_invoice.wsgi:application --bind 0.0.0.0:$PORT --workers 4 --threads 2 --worker-class gthread --timeout 120
```

#### Advanced Settings
- **Auto-Deploy:** Yes
- **Health Check Path:** `/health/`

### Step 4: Environment Variables

Add these environment variables in Render dashboard:

```env
# Django Configuration
DJANGO_SECRET_KEY=<your-generated-secret-key>
DJANGO_ENV=production
DEBUG=False
PYTHON_VERSION=3.11.0

# Database (Render provides this)
DATABASE_URL=<paste-internal-database-url>

# Site Configuration
SITE_URL=https://your-app-name.onrender.com
DJANGO_ALLOWED_HOSTS=your-app-name.onrender.com,.onrender.com
CSRF_TRUSTED_ORIGINS=https://your-app-name.onrender.com,https://*.onrender.com

# Paystack (Production Keys)
PAYSTACK_PUBLIC_KEY=pk_live_xxxxxxxxxxxxxxxx
PAYSTACK_SECRET_KEY=sk_live_xxxxxxxxxxxxxxxx
PAYSTACK_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxxxxx

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com

# WhatsApp
WHATSAPP_NUMBER=2348012345678

# Twilio (Optional)
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxx
TWILIO_WHATSAPP_NUMBER=+14155238886
```

### Step 5: Deploy

1. Click **Create Web Service**
2. Render will:
   - Clone your repository
   - Install dependencies via `build.sh`
   - Run migrations (`python manage.py migrate`)
   - Collect static files
   - Start Gunicorn server
3. Monitor build logs for any errors
4. Access your app at `https://your-app-name.onrender.com`

### Step 6: Configure Paystack Webhook

1. Log in to [Paystack Dashboard](https://dashboard.paystack.com)
2. Go to **Settings** → **API Keys & Webhooks**
3. Add webhook URL:
   ```
   https://your-app-name.onrender.com/api/paystack/webhook/
   ```
4. Select events: `charge.success` and `charge.failed`
5. Copy the **Webhook Secret** and update your Render environment variable

### Step 7: Create Superuser

```bash
# Using Render Shell (Dashboard → Shell tab)
python manage.py createsuperuser

# Or via Render CLI
render shell -s smart-invoice
python manage.py createsuperuser
```

---

## 🔧 Replit Deployment

### Step 1: Configure Secrets

1. Open your Repl
2. Go to **Secrets** tab (lock icon in sidebar)
3. Add all environment variables from `.env.example`

**Critical Secrets:**
```env
DJANGO_SECRET_KEY=<generated-key>
PAYSTACK_PUBLIC_KEY=pk_live_xxx
PAYSTACK_SECRET_KEY=sk_live_xxx
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Step 2: Update Settings

Already configured! The project uses:
- `smart_invoice/settings/dev.py` for development
- Automatic environment detection
- CSRF trusted origins for `.replit.dev` and `.repl.co`

### Step 3: Deploy

1. Click **Run** button to start development server
2. For production deployment:
   - Go to **Deployments** tab
   - Click **Deploy**
   - Choose deployment type:
     - **Autoscale:** Best for stateless apps (default)
     - **Reserved VM:** For apps needing persistent state
3. Configure custom domain (optional):
   - Add your domain in Deployments settings
   - Update DNS records as instructed

### Step 4: Database

Replit automatically provisions PostgreSQL for deployments. No additional setup needed!

---

## 🐳 Docker Deployment

### Local Docker Setup

```bash
# 1. Build and start services
docker-compose up -d

# 2. Run migrations
docker-compose exec web python manage.py migrate

# 3. Create superuser
docker-compose exec web python manage.py createsuperuser

# 4. Collect static files (if needed)
docker-compose exec web python manage.py collectstatic --noinput

# 5. View logs
docker-compose logs -f web
```

Access at `http://localhost:5000`

### Production Docker Deployment

**Build production image:**
```bash
docker build -t smart-invoice:latest .
```

**Run with environment variables:**
```bash
docker run -d \
  --name smart-invoice \
  -p 5000:5000 \
  -e DJANGO_SECRET_KEY="your-secret-key" \
  -e DATABASE_URL="postgresql://..." \
  -e PAYSTACK_PUBLIC_KEY="pk_live_..." \
  -e PAYSTACK_SECRET_KEY="sk_live_..." \
  -e EMAIL_HOST_USER="email@example.com" \
  -e EMAIL_HOST_PASSWORD="password" \
  smart-invoice:latest
```

**Or use docker-compose with .env file:**
```bash
# Create .env file with production variables
docker-compose -f docker-compose.prod.yml up -d
```

---

## 🖥️ Custom Server Deployment

### System Requirements

- Ubuntu 20.04 LTS or newer
- Python 3.11+
- PostgreSQL 14+
- Nginx
- Supervisor (for process management)

### Step 1: Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3.11 python3.11-venv python3-pip postgresql postgresql-contrib nginx supervisor git

# Install Node.js 18+
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
```

### Step 2: PostgreSQL Setup

```bash
# Create database and user
sudo -u postgres psql
CREATE DATABASE smartinvoice;
CREATE USER smartinvoice_user WITH PASSWORD 'secure_password_here';
ALTER ROLE smartinvoice_user SET client_encoding TO 'utf8';
ALTER ROLE smartinvoice_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE smartinvoice_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE smartinvoice TO smartinvoice_user;
\q
```

### Step 3: Application Setup

```bash
# Create app directory
sudo mkdir -p /var/www/smart-invoice
sudo chown $USER:$USER /var/www/smart-invoice
cd /var/www/smart-invoice

# Clone repository
git clone <your-repo-url> .

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Install Node dependencies and build CSS
npm install
npm run build:css

# Create .env file
cp .env.example .env
nano .env  # Edit with your production values

# Run migrations
python manage.py migrate --settings=smart_invoice.settings.prod

# Collect static files
python manage.py collectstatic --noinput --settings=smart_invoice.settings.prod

# Create superuser
python manage.py createsuperuser --settings=smart_invoice.settings.prod
```

### Step 4: Gunicorn Setup

Create `/etc/supervisor/conf.d/smart-invoice.conf`:

```ini
[program:smart-invoice]
command=/var/www/smart-invoice/venv/bin/gunicorn smart_invoice.wsgi:application --bind 127.0.0.1:8000 --workers 4 --threads 2 --timeout 120
directory=/var/www/smart-invoice
user=www-data
autostart=true
autorestart=true
stdout_logfile=/var/log/smart-invoice/gunicorn.log
stderr_logfile=/var/log/smart-invoice/gunicorn.err.log
environment=DJANGO_SETTINGS_MODULE="smart_invoice.settings.prod"
```

```bash
# Create log directory
sudo mkdir -p /var/log/smart-invoice
sudo chown www-data:www-data /var/log/smart-invoice

# Update supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start smart-invoice
```

### Step 5: Nginx Configuration

Create `/etc/nginx/sites-available/smart-invoice`:

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;
    
    # SSL Configuration (use Certbot to generate)
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    
    # Static files
    location /static/ {
        alias /var/www/smart-invoice/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Media files
    location /media/ {
        alias /var/www/smart-invoice/media/;
        expires 1y;
        add_header Cache-Control "public";
    }
    
    # Proxy to Gunicorn
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        client_max_body_size 10M;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/smart-invoice /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Step 6: SSL Certificate

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Auto-renewal is configured automatically
```

---

## 📊 Post-Deployment Steps

### 1. Verify Deployment

```bash
# Run deployment checks
python manage.py check --deploy

# Test health endpoint
curl https://your-domain.com/health/
```

### 2. Create Admin Account

```bash
python manage.py createsuperuser
```

### 3. Configure Monitoring

**Sentry (Recommended):**
1. Sign up at [sentry.io](https://sentry.io)
2. Create new Django project
3. Add `SENTRY_DSN` to environment variables
4. Sentry automatically captures errors

**Alternative: Simple logging**
```python
# Already configured in settings/prod.py
# Logs are sent to console (viewable in Render/Heroku dashboard)
```

### 4. Set Up Backups

**Render:**
- Automatic daily backups included
- Manual backups via dashboard

**Custom Server:**
```bash
# Create backup script
cat > /usr/local/bin/backup-db.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/var/backups/smart-invoice"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR
pg_dump smartinvoice | gzip > $BACKUP_DIR/backup_$DATE.sql.gz
find $BACKUP_DIR -mtime +7 -delete  # Keep 7 days
EOF

chmod +x /usr/local/bin/backup-db.sh

# Add to crontab (daily at 2 AM)
crontab -e
0 2 * * * /usr/local/bin/backup-db.sh
```

---

## 📈 Monitoring & Maintenance

### Health Checks

Access `/health/` endpoint to verify:
- Database connectivity
- Cache system
- Email configuration
- Paystack configuration

### Logs

**Render:**
```
Dashboard → Logs tab
```

**Docker:**
```bash
docker-compose logs -f web
```

**Custom Server:**
```bash
sudo tail -f /var/log/smart-invoice/gunicorn.log
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Performance Monitoring

1. Enable Django Debug Toolbar (dev only)
2. Monitor response times in logs
3. Check database query performance
4. Monitor Gunicorn worker status

---

## 🔧 Troubleshooting

### Static Files Not Loading

```bash
# Re-collect static files
python manage.py collectstatic --clear --noinput

# Rebuild CSS
npm run build:css
```

### Database Connection Issues

```bash
# Test connection
python manage.py dbshell

# Check DATABASE_URL format:
postgresql://username:password@hostname:5432/database_name
```

### Paystack Webhook Not Working

1. Verify webhook URL is publicly accessible
2. Check `PAYSTACK_WEBHOOK_SECRET` matches dashboard
3. Monitor webhook logs:
   ```bash
   # View webhook requests
   tail -f logs/django.log | grep webhook
   ```

### Performance Issues

```bash
# Check Gunicorn workers
sudo supervisorctl status smart-invoice

# Restart if needed
sudo supervisorctl restart smart-invoice

# Monitor database queries (enable query logging)
LOGGING['loggers']['django.db.backends']['level'] = 'DEBUG'
```

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/your-repo/issues)
- **Documentation:** `/faq/` and this guide
- **Email:** Contact via support form

---

**Built with ❤️ by Jeffery Onome** | [Portfolio](https://onome-portfolio-ten.vercel.app)
