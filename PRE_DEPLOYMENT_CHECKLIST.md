# Pre-Deployment Checklist for Smart Invoice

## ✅ Completed Production-Ready Fixes

### Security & Configuration Fixes
- [x] Removed `whitenoise` from `INSTALLED_APPS` (kept only in MIDDLEWARE)
- [x] Set `CSRF_COOKIE_HTTPONLY = True` for security
- [x] Removed file logging handler (console-only for Render's ephemeral filesystem)
- [x] Cleaned requirements.txt - removed all duplicates
- [x] Added version to `twilio` package (9.8.4)
- [x] Removed duplicate entries for `python-dateutil`, `django-stubs`, `django-stubs-ext`
- [x] Alphabetized requirements.txt for maintainability
- [x] Updated .gitignore to include `db.sqlite3`
- [x] Removed unused `HttpResponse` import then re-added (actually needed for PDF generation)
- [x] Cleaned up Python cache files and __pycache__ directories

### Build & Deployment Configuration
- [x] Verified build.sh is correct for Render
- [x] Confirmed render.yaml has proper configuration
- [x] TailwindCSS builds successfully without errors
- [x] Django system check passes with no issues
- [x] No debug code (print statements, console.log, TODO comments) found

## ⚠️ CRITICAL: Manual Actions Required Before Deployment

### 1. Remove Tracked Files from Git (REQUIRED)

The following files are currently tracked in git but should not be deployed:

```bash
# Remove db.sqlite3 from git tracking (it's a development database)
git rm --cached db.sqlite3

# Remove staticfiles directory from git tracking (generated during build)
git rm -r --cached staticfiles/

# Commit the removal
git add .gitignore
git commit -m "Remove db.sqlite3 and staticfiles from version control"
```

**Why this is critical:**
- `db.sqlite3` contains development data and should never be deployed
- `staticfiles/` will be generated fresh during Render's build process
- Committing these files poses security and operational risks

### 2. Verify Render Environment Variables

Before deploying, ensure ALL required environment variables are set in Render Dashboard:

#### Required (Application won't work without these):
```bash
DJANGO_SECRET_KEY=<generate-new-secure-key>
DJANGO_ENV=production
DJANGO_DEBUG=False
DATABASE_URL=<auto-provided-by-render>
DJANGO_ALLOWED_HOSTS=<your-app>.onrender.com
```

#### Required for Features:
```bash
# Payment Processing (required for Paystack)
PAYSTACK_PUBLIC_KEY=pk_live_xxxxx
PAYSTACK_SECRET_KEY=sk_live_xxxxx
PAYSTACK_CALLBACK_URL=https://<your-app>.onrender.com/payment/callback/

# Email Notifications (required for email features)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=<gmail-app-password>

# WhatsApp Integration (optional)
TWILIO_ACCOUNT_SID=<your-twilio-sid>
TWILIO_AUTH_TOKEN=<your-twilio-token>
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
```

#### Optional (Performance Enhancement):
```bash
# Redis for better rate limiting (recommended for production)
REDIS_URL=redis://your-redis-url:6379/0

# CSRF Trusted Origins (if using custom domain)
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://<your-app>.onrender.com
```

### 3. Generate Secure Django Secret Key

**DO NOT use the default secret key in production!**

Generate a new one:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy the output and set it as `DJANGO_SECRET_KEY` in Render.

### 4. Configure Paystack Webhook

After deployment:
1. Go to [Paystack Dashboard](https://dashboard.paystack.com)
2. Navigate to Settings → Webhooks
3. Add webhook URL: `https://<your-app>.onrender.com/payment/webhook/`
4. Test the webhook to ensure it's receiving events

## 📋 Deployment Steps

### Step 1: Clean Up Git Repository
```bash
# Execute the git commands from section 1 above
git rm --cached db.sqlite3
git rm -r --cached staticfiles/
git add .gitignore
git commit -m "Remove development files from version control"
git push origin main
```

### Step 2: Deploy to Render

1. **Create Web Service**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Render will auto-detect `render.yaml` configuration

2. **Create PostgreSQL Database**
   - Click "New +" → "PostgreSQL"
   - Name: `smart-invoice-db`
   - Region: Same as your web service
   - Plan: Starter (recommended) or Free (testing)
   - The `DATABASE_URL` will be automatically linked

3. **Configure Environment Variables**
   - Add all variables from section 2 above
   - Double-check all API keys and secrets are correct
   - Ensure `DJANGO_ALLOWED_HOSTS` includes your Render URL

4. **Deploy**
   - Click "Create Web Service" or "Manual Deploy"
   - Monitor build logs for any errors
   - Wait for "Live" status (typically 3-5 minutes)

### Step 3: Post-Deployment

1. **Create Admin Account**
   ```bash
   # In Render Shell
   python manage.py createsuperuser
   ```

2. **Verify Health Checks**
   - Visit: `https://<your-app>.onrender.com/health/`
   - Should return: "healthy" with 200 status

3. **Test Core Features**
   - Login to admin panel
   - Create a test invoice
   - Generate PDF
   - Test payment flow (if Paystack configured)

## 🔒 Production Security Checklist

- [ ] `DEBUG = False` in production
- [ ] New `DJANGO_SECRET_KEY` generated and set
- [ ] `ALLOWED_HOSTS` properly configured
- [ ] All API keys are live keys (not test keys)
- [ ] HTTPS enforced (automatic on Render)
- [ ] HSTS enabled (already configured)
- [ ] CSRF protection enabled (already configured)
- [ ] Database uses PostgreSQL (not SQLite)
- [ ] No secrets committed to git
- [ ] `.env` file (if exists) is in .gitignore
- [ ] Paystack webhook URL configured
- [ ] Email credentials are app-specific passwords

## 🚀 What's Already Configured

✅ **Backend:**
- Django 5.2.7 with production settings
- PostgreSQL database support with connection pooling
- WhiteNoise for static file serving
- Gunicorn WSGI server (4 workers, 2 threads)
- Security middleware (HSTS, CSP, XSS protection)
- Rate limiting middleware (60 req/min)
- Audit logging for sensitive operations

✅ **Frontend:**
- TailwindCSS with optimized build
- Modern glassmorphism UI design
- Responsive mobile-first design
- Professional error pages (404, 500, 403)
- Toast notification system

✅ **Features:**
- Complete invoice management (CRUD)
- PDF generation and download
- Email invoice delivery
- WhatsApp invoice sharing
- Paystack payment processing
- Client management
- Analytics dashboard
- CSV exports

✅ **Infrastructure:**
- Automated migrations (pre-deploy)
- Cache table creation (pre-deploy)
- Overdue invoice checks (pre-deploy)
- Health check endpoints
- Management commands for automation

## 📊 Expected Build Output

When deploying to Render, you should see:

```
===== Starting Build Process =====
Installing Node.js dependencies...
Building Tailwind CSS...
Done in 1001ms.
Installing Python dependencies...
Collecting static files...
52 static files copied to '/opt/render/project/src/staticfiles'
===== Build Process Complete =====
Running migrations...
Operations to perform: ...
Applying ...
Creating cache table...
Checking overdue invoices...
Starting Gunicorn...
[INFO] Listening at: http://0.0.0.0:10000
```

## ⚠️ Common Deployment Issues & Solutions

### Issue: Build Fails
**Solution:** Check build logs for specific error, verify all dependencies in requirements.txt

### Issue: Static Files Not Loading
**Solution:** Verify `collectstatic` ran successfully in build logs, check browser console

### Issue: Database Connection Error
**Solution:** Verify `DATABASE_URL` is set, check PostgreSQL database is running

### Issue: Payment Not Working
**Solution:** Verify Paystack keys are live keys, webhook URL is configured

### Issue: CSRF Verification Failed
**Solution:** Add your domain to `CSRF_TRUSTED_ORIGINS` in Render environment variables

## 📞 Support

- **Django Docs:** https://docs.djangoproject.com/
- **Render Docs:** https://render.com/docs
- **Paystack Docs:** https://paystack.com/docs

---

**After completing this checklist, your Smart Invoice application will be production-ready and deployed on Render! 🎉**
