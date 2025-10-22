# Smart Invoice - Render Deployment Guide

## Overview
This guide provides step-by-step instructions for deploying Smart Invoice to Render.com.

## Prerequisites
- Render.com account
- GitHub repository with the Smart Invoice code
- Paystack account (optional, for payment processing)
- SMTP email credentials (optional, for email functionality)

## Deployment Steps

### 1. Database Setup
1. Log in to your Render dashboard
2. Click "New +" and select "PostgreSQL"
3. Configure:
   - Name: `smart-invoice-db`
   - Region: Choose closest to your users
   - Plan: Free or Starter based on needs
4. Click "Create Database"
5. Copy the "Internal Database URL" for later use

### 2. Web Service Setup
1. Click "New +" and select "Web Service"
2. Connect your GitHub repository
3. Configure the service:
   - **Name**: `smart-invoice`
   - **Region**: Same as database
   - **Branch**: `main`
   - **Root Directory**: Leave blank
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --no-input && python manage.py migrate`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT --reuse-port --workers 4 smart_invoice.wsgi:application`
   - **Plan**: Free or Starter

### 3. Environment Variables
Add the following environment variables in Render dashboard:

#### Required Variables
```
DJANGO_SECRET_KEY=<generate-a-secure-random-key>
DATABASE_URL=<your-render-postgres-internal-url>
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=<your-app-name>.onrender.com
```

#### Optional - Payment Integration
```
PAYSTACK_SECRET_KEY=<your-paystack-secret-key>
PAYSTACK_PUBLIC_KEY=<your-paystack-public-key>
```

#### Optional - Email Configuration
```
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=<your-email@gmail.com>
EMAIL_HOST_PASSWORD=<your-app-password>
```

#### Optional - Twilio/WhatsApp
```
TWILIO_ACCOUNT_SID=<your-twilio-sid>
TWILIO_AUTH_TOKEN=<your-twilio-token>
TWILIO_WHATSAPP_NUMBER=<your-whatsapp-number>
```

### 4. Generating Django Secret Key
Run this Python command to generate a secure secret key:
```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 5. Deploy
1. Click "Create Web Service"
2. Render will automatically build and deploy your application
3. Monitor the deployment logs for any errors
4. Once deployed, your app will be available at `https://<your-app-name>.onrender.com`

### 6. Post-Deployment Setup

#### Create Superuser
1. Go to Render dashboard → Your service → Shell
2. Run: `python manage.py createsuperuser`
3. Follow the prompts to create an admin account

#### Access Admin Panel
- Visit: `https://<your-app-name>.onrender.com/admin`
- Login with superuser credentials

### 7. Configure Paystack Webhook (Optional)
1. Log in to your Paystack dashboard
2. Go to Settings → Webhooks
3. Add webhook URL: `https://<your-app-name>.onrender.com/payment/webhook/`
4. Save the webhook URL

## Production Checklist

- [ ] Database created and connected
- [ ] All environment variables set
- [ ] Django secret key generated and added
- [ ] DEBUG set to False
- [ ] Allowed hosts configured
- [ ] Static files collected
- [ ] Database migrations applied
- [ ] Superuser created
- [ ] Admin panel accessible
- [ ] Payment integration tested (if using Paystack)
- [ ] Email sending tested (if configured)
- [ ] SSL certificate active (automatic on Render)

## Monitoring and Maintenance

### View Logs
- Render Dashboard → Your Service → Logs
- Monitor for errors and performance issues

### Database Backups
- Render automatically backs up PostgreSQL databases
- Configure backup frequency in database settings

### Scaling
- Upgrade to paid plan for:
  - More database storage
  - Higher memory/CPU
  - Multiple workers
  - Auto-scaling

## Troubleshooting

### Static Files Not Loading
- Ensure `collectstatic` runs in build command
- Check STATIC_ROOT and STATIC_URL settings
- Verify WhiteNoise is in MIDDLEWARE

### Database Connection Errors
- Verify DATABASE_URL is set correctly
- Check database status in Render dashboard
- Ensure migrations have run

### 500 Errors
- Check logs in Render dashboard
- Verify all environment variables are set
- Ensure DEBUG=False in production
- Check ALLOWED_HOSTS includes your domain

## Features Deployed

### Core Features
- Invoice creation, editing, and management
- PDF invoice generation
- Multi-currency support
- Payment terms configuration

### Payment Integration
- Paystack payment processing
- Payment verification
- Webhook support for real-time updates
- Payment history tracking
- WhatsApp payment links

### Analytics & Reporting
- Revenue dashboard
- Client analytics
- Payment statistics
- Monthly revenue trends
- CSV exports (invoices, payments, clients)

### Client Management
- Customer database
- Invoice history per client
- Revenue tracking per client
- Automated client linking

### Admin Features
- Comprehensive admin panel
- Client management
- Payment transaction viewing
- Support inquiry management
- Bulk actions and filtering

## Security Features

- HTTPS enforced (Render provides free SSL)
- Secure session cookies
- CSRF protection
- HSTS enabled
- Password hashing
- SQL injection prevention (Django ORM)
- XSS protection

## Performance Optimizations

- Database indexing on frequently queried fields
- WhiteNoise for efficient static file serving
- Gunicorn with multiple workers
- Connection pooling for database
- Query optimization in analytics

## Support

For issues or questions:
- Check Render documentation: https://render.com/docs
- Review Django deployment guide: https://docs.djangoproject.com/en/5.2/howto/deployment/
- Contact support via the support page on your deployed app

## Notes

- Free tier on Render may spin down after inactivity (first request may be slow)
- Consider upgrading to paid tier for production use
- Regular backups recommended for critical data
- Monitor usage and costs in Render dashboard
