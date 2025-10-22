# Smart Invoice - Render Deployment Guide

This guide will help you deploy Smart Invoice to Render.com

## Prerequisites

- A Render account (https://render.com)
- GitHub/GitLab repository with this code
- Paystack account (optional - for payment features)
- Twilio account (optional - for WhatsApp features)

## Step 1: Push Your Code to Git

Make sure all your code is pushed to GitHub, GitLab, or another Git provider that Render supports.

## Step 2: Create a New Web Service on Render

1. Log in to your Render Dashboard
2. Click "New +" button and select "Web Service"
3. Connect your Git repository
4. Configure the following settings:

### Basic Settings

- **Name**: `smart-invoice` (or your preferred name)
- **Region**: Choose closest to your users
- **Branch**: `main` (or your default branch)
- **Root Directory**: Leave empty
- **Runtime**: `Python 3`

### Build & Deploy Settings

- **Build Command**: `./build.sh`
- **Start Command**: `gunicorn smart_invoice.wsgi:application --bind 0.0.0.0:$PORT`

### Instance Type

- **Free** tier works for testing
- **Starter** or higher recommended for production

## Step 3: Add Environment Variables

In the Render dashboard, go to "Environment" and add these variables:

### Required Variables

```
DJANGO_SECRET_KEY=<generate-a-long-random-string>
DJANGO_DEBUG=False
PYTHON_VERSION=3.11.0
```

### Optional Variables (for full functionality)

#### Paystack Payment Integration
```
PAYSTACK_PUBLIC_KEY=<your-paystack-public-key>
PAYSTACK_SECRET_KEY=<your-paystack-secret-key>
PAYSTACK_CALLBACK_URL=https://your-app-name.onrender.com/invoice/payment/callback/
```

#### Twilio WhatsApp Integration
```
TWILIO_ACCOUNT_SID=<your-twilio-account-sid>
TWILIO_AUTH_TOKEN=<your-twilio-auth-token>
TWILIO_WHATSAPP_NUMBER=<your-whatsapp-number>
```

#### Email Configuration (Optional - SMTP)
```
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=<your-email@gmail.com>
EMAIL_HOST_PASSWORD=<your-app-password>
```

## Step 4: Add PostgreSQL Database

1. In your Render service, go to the "Environment" tab
2. Render will automatically create a `DATABASE_URL` environment variable when you add a PostgreSQL database
3. Or create a separate PostgreSQL database and link it

To add a database:
1. Click "New +" → "PostgreSQL"
2. Give it a name (e.g., `smart-invoice-db`)
3. Select a plan (Free tier available)
4. Once created, go back to your web service
5. Go to "Environment" → scroll to "Environment Variables"
6. The `DATABASE_URL` should already be linked automatically

## Step 5: Deploy!

1. Click "Create Web Service" or "Manual Deploy"
2. Render will:
   - Install Node.js dependencies
   - Build Tailwind CSS
   - Install Python dependencies
   - Collect static files
   - Run database migrations
   - Start the application

## Step 6: Post-Deployment

### Create a Superuser (Admin Account)

Once deployed, open the Render Shell and run:

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

### Access Your Application

- **Main App**: `https://your-app-name.onrender.com`
- **Admin Panel**: `https://your-app-name.onrender.com/admin`

## Important Notes

### Free Tier Limitations

- Free tier spins down after 15 minutes of inactivity
- First request after spin-down may take 30-60 seconds
- Upgrade to paid tier for always-on service

### Database Backups

- Render automatically backs up PostgreSQL databases
- Free tier: Daily backups (7-day retention)
- Paid tiers: More frequent backups with longer retention

### Static Files

- Static files are served via WhiteNoise (already configured)
- No need for external CDN for basic usage
- CSS is pre-compiled and minified

### Security Best Practices

1. **Always set `DJANGO_DEBUG=False` in production**
2. **Use a strong SECRET_KEY** (generate with: `python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'`)
3. **Never commit secrets** to Git
4. **Enable HTTPS** (Render provides free SSL certificates)

## Troubleshooting

### Build Fails

- Check build logs in Render dashboard
- Ensure `build.sh` is executable: `chmod +x build.sh`
- Verify Node.js and Python versions

### Database Errors

- Ensure `DATABASE_URL` environment variable is set
- Check PostgreSQL database is running
- Verify migrations ran successfully in build logs

### Static Files Not Loading

- Check that `python manage.py collectstatic` ran in build log
- Verify WhiteNoise is in `INSTALLED_APPS` and `MIDDLEWARE`
- Check browser console for 404 errors

### Payment/WhatsApp Not Working

- Verify environment variables are set correctly
- Check Paystack/Twilio dashboard for API key validity
- Ensure callback URLs are correct

## Updating Your Application

1. Push changes to your Git repository
2. Render will automatically detect changes and redeploy
3. Or manually trigger a deploy from the Render dashboard

## Monitoring

- View logs in real-time from Render dashboard
- Set up email/Slack notifications for deploy status
- Monitor database usage in PostgreSQL dashboard

## Cost Estimates

### Free Tier
- Web Service: $0
- PostgreSQL: $0
- Total: **$0/month**

### Production Tier (Recommended)
- Web Service (Starter): $7/month
- PostgreSQL (Starter): $7/month
- Total: **$14/month**

---

## Need Help?

- Render Docs: https://render.com/docs
- Django Deployment: https://docs.djangoproject.com/en/5.2/howto/deployment/
- Contact Developer: Built by Jeffery Onome — https://onome-portfolio-ten.vercel.app

