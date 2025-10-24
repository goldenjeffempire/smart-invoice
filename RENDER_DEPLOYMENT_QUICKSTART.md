# 🚀 Render Deployment - Quick Start Guide

**Deploy Smart Invoice to production in under 10 minutes.**

---

## Prerequisites

- GitHub account (to host your repository)
- Render account (free tier available at https://render.com)
- Paystack account with live API keys
- Gmail app password for email notifications

---

## Step 1: Push to GitHub

```bash
# Initialize git (if not already done)
git init
git add .
git commit -m "Smart Invoice - Production Ready"

# Create a new repository on GitHub
# Then push your code
git remote add origin https://github.com/your-username/smart-invoice.git
git branch -M main
git push -u origin main
```

---

## Step 2: Create Render Account

1. Go to https://render.com
2. Click "Get Started for Free"
3. Sign up with GitHub (easiest option)

---

## Step 3: Deploy to Render

### Option A: Using render.yaml (Recommended - Fastest)

1. **Connect Repository**
   - Click "New" → "Blueprint"
   - Connect your GitHub repository
   - Render auto-detects `render.yaml`
   - Click "Apply"

2. **Configure Environment Variables**
   
   Render will create the services. Now add these environment variables in the Web Service settings:

   **Required Variables:**
   ```
   DJANGO_ALLOWED_HOSTS=.onrender.com
   CSRF_TRUSTED_ORIGINS=https://your-app-name.onrender.com
   PAYSTACK_PUBLIC_KEY=pk_live_xxxxxxxxxxxxx
   PAYSTACK_SECRET_KEY=sk_live_xxxxxxxxxxxxx
   PAYSTACK_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxx
   WHATSAPP_NUMBER=2348xxxxxxxxx
   SITE_URL=https://your-app-name.onrender.com
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-gmail-app-password
   ```

   **Optional Variables:**
   ```
   TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxx
   TWILIO_AUTH_TOKEN=xxxxxxxxxxxxx
   TWILIO_WHATSAPP_NUMBER=+14155238886
   DEFAULT_FROM_EMAIL=your-email@gmail.com
   ```

3. **Deploy**
   - Render automatically builds and deploys
   - Wait 3-5 minutes for first deployment
   - Monitor build logs for any errors

### Option B: Manual Setup

1. **Create Web Service**
   - Click "New" → "Web Service"
   - Connect GitHub repository
   - Configure:
     ```
     Name: smart-invoice
     Environment: Python 3
     Build Command: ./build.sh
     Start Command: gunicorn smart_invoice.wsgi:application --bind 0.0.0.0:$PORT
     ```

2. **Create PostgreSQL Database**
   - Click "New" → "PostgreSQL"
   - Name: smart-invoice-db
   - Plan: Starter (free)
   - Copy Internal Database URL

3. **Link Database to Web Service**
   - Go to Web Service → Environment
   - Add: `DATABASE_URL` = (paste Internal Database URL)

4. **Add Environment Variables** (same as above)

---

## Step 4: Configure Paystack Webhook

1. **Get Your Render URL**
   - After deployment, copy your app URL: `https://your-app-name.onrender.com`

2. **Configure in Paystack**
   - Login to Paystack Dashboard
   - Go to Settings → API Keys & Webhooks
   - Click "Add Webhook Endpoint"
   - Webhook URL: `https://your-app-name.onrender.com/api/paystack/webhook/`
   - Select Events: `charge.success`, `charge.failed`
   - Click "Add Webhook"
   - Copy the Webhook Secret

3. **Update Render Environment**
   - Go back to Render → Your Web Service → Environment
   - Update: `PAYSTACK_WEBHOOK_SECRET` = (paste webhook secret)
   - Click "Save Changes" (this triggers redeploy)

---

## Step 5: Setup Automated Tasks (Optional)

For invoice reminders and monthly reports:

1. **Create Cron Job for Invoice Reminders**
   - Click "New" → "Cron Job"
   - Name: invoice-reminders
   - Command: `python manage.py send_invoice_reminders`
   - Schedule: `0 9 * * *` (Daily at 9 AM UTC)

2. **Create Cron Job for Monthly Reports**
   - Click "New" → "Cron Job"
   - Name: monthly-reports
   - Command: `python manage.py generate_invoice_reports --email`
   - Schedule: `0 10 1 * *` (1st of month at 10 AM UTC)

---

## Step 6: Create Superuser

1. **Open Shell in Render**
   - Go to your Web Service
   - Click "Shell" tab
   - Run:
     ```bash
     python manage.py createsuperuser
     ```
   - Enter username, email, password

2. **Access Admin**
   - Visit: `https://your-app-name.onrender.com/admin/`
   - Login with superuser credentials

---

## Step 7: Verify Deployment

### Test Health Check
```bash
curl https://your-app-name.onrender.com/health/
```

Expected response:
```json
{
  "status": "healthy",
  "checks": {
    "database": {"passing": true},
    "cache": {"passing": true},
    "paystack": {"passing": true},
    "email": {"passing": true}
  }
}
```

### Test Application
1. Visit `https://your-app-name.onrender.com`
2. Create an account
3. Create a test invoice
4. Test payment flow with Paystack test card

---

## Troubleshooting

### Build Fails

**Check build logs:**
- Render Dashboard → Your Service → Events → View Logs

**Common issues:**
1. **Missing dependencies** - Check `requirements.txt`
2. **Static files** - Ensure `npm run build:css` runs successfully
3. **Python version** - Verify `runtime.txt` has `python-3.11.0`

**Solution:**
```bash
# Verify locally first
./build.sh
python manage.py check --deploy
```

### Database Connection Errors

**Check:**
1. DATABASE_URL is set correctly (Internal URL from Render Postgres)
2. Database service is running
3. Web service has access to database

**Fix:**
- Render Dashboard → Database → Connections → Check Internal URL
- Update `DATABASE_URL` in Web Service environment

### Static Files Not Loading

**Solution:**
```bash
# In Render Shell
python manage.py collectstatic --no-input --clear
```

Or redeploy (build.sh runs this automatically)

### Paystack Webhook Not Working

**Check:**
1. Webhook URL is publicly accessible
2. `PAYSTACK_WEBHOOK_SECRET` matches Paystack dashboard
3. Events `charge.success` and `charge.failed` are selected

**Test:**
```bash
# Check logs in Render
grep "webhook" /var/log/app.log
```

### Email Not Sending

**For Gmail:**
1. Enable 2-Factor Authentication
2. Generate App Password (not regular password)
3. Use App Password in `EMAIL_HOST_PASSWORD`

**Verify:**
```bash
# In Render Shell
python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'Message', 'from@example.com', ['to@example.com'])
```

---

## Performance Optimization

### Enable Redis Caching (Optional but Recommended)

1. **Add Redis Add-on**
   - Render Dashboard → Your Service → Add Redis
   - Copy Redis URL

2. **Update Environment**
   - Add: `REDIS_URL` = (Redis URL from above)
   - Redeploy

This improves rate limiting and caching performance.

### Scale Workers

For higher traffic:
- Render Dashboard → Your Service → Settings
- Increase to Standard plan
- Adjust worker count in `render.yaml`:
  ```yaml
  startCommand: "gunicorn ... --workers 8 --threads 4 ..."
  ```

---

## Custom Domain (Optional)

1. **Add Custom Domain in Render**
   - Your Service → Settings → Custom Domains
   - Add your domain (e.g., `smartinvoice.yourdomain.com`)

2. **Update DNS**
   - Add CNAME record in your DNS provider:
     ```
     CNAME smartinvoice.yourdomain.com -> your-app-name.onrender.com
     ```

3. **Update Environment Variables**
   ```
   DJANGO_ALLOWED_HOSTS=yourdomain.com,.onrender.com
   CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://*.onrender.com
   SITE_URL=https://smartinvoice.yourdomain.com
   ```

4. **Update Paystack Webhook**
   - Change webhook URL to: `https://smartinvoice.yourdomain.com/api/paystack/webhook/`

---

## Monitoring

### View Logs
```bash
# Real-time logs
Render Dashboard → Your Service → Logs

# Search logs
# Click "Search Logs" and filter by time/keyword
```

### Setup Alerts

1. **Email Notifications**
   - Render Dashboard → Account → Notifications
   - Enable deployment failure alerts

2. **External Monitoring** (Recommended)
   - Use UptimeRobot (free): https://uptimerobot.com
   - Monitor: `https://your-app-name.onrender.com/health/`
   - Get alerts for downtime

---

## Backup Strategy

### Database Backups

Render automatically backs up PostgreSQL databases, but for extra safety:

1. **Manual Backup**
   ```bash
   # In Render Shell
   pg_dump $DATABASE_URL > backup.sql
   ```

2. **Automated Backups** (use Render's built-in feature)
   - PostgreSQL plans include automatic backups
   - Free tier: 1 day retention
   - Paid tiers: 7+ days retention

---

## Cost Estimate

**Free Tier:**
- Web Service: Free (with sleep after inactivity)
- PostgreSQL: Free Starter plan
- Total: **$0/month**

**Production Tier:**
- Web Service: $7/month (Standard plan, always on)
- PostgreSQL: $7/month (Starter plan)
- Redis (optional): $3/month
- Total: **$14-17/month**

---

## Post-Deployment Checklist

- [ ] Application accessible at Render URL
- [ ] Health check returns "healthy" status
- [ ] Admin panel accessible
- [ ] Can create and view invoices
- [ ] Paystack payment test successful
- [ ] Webhook receiving Paystack events
- [ ] Email notifications working
- [ ] WhatsApp Pay Now button works
- [ ] Static files loading correctly
- [ ] Custom domain configured (if applicable)
- [ ] Monitoring/alerts set up
- [ ] Cron jobs running (check logs)

---

## Quick Commands Reference

```bash
# View deployment logs
render logs

# SSH into container
render shell

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --no-input

# Send test invoice reminder
python manage.py send_invoice_reminders --dry-run

# Generate monthly report
python manage.py generate_invoice_reports --month 10 --year 2025

# Check deployment readiness
python manage.py check --deploy

# Test health endpoint
curl https://your-app-name.onrender.com/health/
```

---

## Support

- **Render Docs**: https://render.com/docs
- **Render Community**: https://community.render.com
- **Smart Invoice Docs**: See README.md and PRODUCTION_DEPLOYMENT.md

---

## Success! 🎉

Your Smart Invoice platform is now live and production-ready on Render!

**Next Steps:**
1. Create your first invoice
2. Test the complete payment flow
3. Share your platform URL with clients
4. Monitor performance and logs
5. Set up custom domain (optional)

Built with ❤️ by [Jeffery Onome](https://onome-portfolio-ten.vercel.app/)
