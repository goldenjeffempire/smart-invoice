# Smart Invoice - Render Deployment Guide

## Prerequisites
- GitHub account
- Render account (free tier available at https://render.com)
- Gmail account for SMTP email sending (optional but recommended)

## Quick Deploy to Render

### Step 1: Push Code to GitHub
```bash
git init
git add .
git commit -m "Initial commit - Smart Invoice SaaS"
git branch -M main
git remote add origin https://github.com/yourusername/smart-invoice.git
git push -u origin main
```

### Step 2: Create New Web Service on Render
1. Log in to [Render Dashboard](https://dashboard.render.com)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure the service:
   - **Name**: `smart-invoice` (or your preferred name)
   - **Environment**: `Python 3`
   - **Build Command**: `chmod +x build.sh && ./build.sh`
   - **Start Command**: `gunicorn smart_invoice.wsgi:application --bind 0.0.0.0:$PORT --workers 4 --timeout 120`

### Step 3: Create PostgreSQL Database
1. In Render Dashboard, click **"New +"** → **"PostgreSQL"**
2. Configure:
   - **Name**: `smart-invoice-db`
   - **Database**: `smart_invoice`
   - **User**: `smart_invoice`
   - **Region**: Same as your web service
3. Click **"Create Database"**
4. Copy the **Internal Database URL** (starts with `postgresql://`)

### Step 4: Configure Environment Variables
In your web service settings, add these environment variables:

#### Required Variables
```
DEBUG=false
SECRET_KEY=<click "Generate" for a secure random key>
DATABASE_URL=<paste your PostgreSQL Internal Database URL>
ALLOWED_HOSTS=.onrender.com,your-app-name.onrender.com
CSRF_TRUSTED_ORIGINS=https://your-app-name.onrender.com,https://*.onrender.com
```

#### Email Configuration (Optional but recommended)
```
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password
DEFAULT_FROM_EMAIL=Smart Invoice <noreply@smartinvoice.com>
```

**Gmail App Password Setup:**
1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Enable 2-Step Verification
3. Go to "App passwords"
4. Generate new app password for "Mail"
5. Copy the 16-character password and use it for `EMAIL_HOST_PASSWORD`

### Step 5: Deploy
1. Click **"Create Web Service"**
2. Wait for the build to complete (5-10 minutes)
3. Once deployed, visit your app at `https://your-app-name.onrender.com`

### Step 6: Create Superuser (Admin Account)
After first deployment:
1. Go to Render Dashboard → Your service → **Shell** tab
2. Run:
```bash
python manage.py createsuperuser
```
3. Follow the prompts to create admin credentials
4. Access admin panel at `https://your-app-name.onrender.com/admin/`

## Using render.yaml (Alternative One-Click Deploy)

This project includes a `render.yaml` file for automated deployment:

1. In Render Dashboard, click **"New +"** → **"Blueprint"**
2. Connect your GitHub repository
3. Render will automatically detect `render.yaml` and create:
   - Web Service (`smart-invoice`)
   - PostgreSQL Database (`smart-invoice-db`)
   - All environment variables

4. You only need to manually set:
   - `EMAIL_HOST_USER` (your Gmail address)
   - `EMAIL_HOST_PASSWORD` (your Gmail app password)
   - Update `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` with your actual Render URL

## Post-Deployment Configuration

### Update URLs in render.yaml
After your first deploy, update these in Render dashboard:
```
ALLOWED_HOSTS=.onrender.com,your-actual-app-name.onrender.com
CSRF_TRUSTED_ORIGINS=https://your-actual-app-name.onrender.com,https://*.onrender.com
```

### Static Files
Static files are automatically handled by WhiteNoise. No additional configuration needed.

### Media Files (Invoice Logos/Branding)
Media files (uploaded logos) are stored in the filesystem. For production persistence:
- Consider using Render Disks (paid feature) or
- Integrate with AWS S3, Cloudinary, or similar cloud storage

## Troubleshooting

### Build Fails
- **WeasyPrint Dependencies**: Ensure `build.sh` installs all system libraries
- **Database Connection**: Verify `DATABASE_URL` is correctly set

### 403 Forbidden on Forms
- **CSRF Error**: Update `CSRF_TRUSTED_ORIGINS` with your actual Render URL
- Must include `https://` prefix

### Email Not Sending
- Verify Gmail App Password is correct
- Check `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD` are set
- Test with password reset feature

### PDF Generation Fails
- Build logs should show successful installation of libpango, libcairo, etc.
- If missing, verify `build.sh` runs `apt-get install` commands

### Static Files Not Loading
- Run `python manage.py collectstatic` in Render Shell if needed
- WhiteNoise should handle this automatically

## Features Checklist

✅ User Authentication (Signup, Login, Logout, Password Reset)  
✅ Multi-Step Invoice Creation  
✅ Dynamic Line Items  
✅ Auto Invoice ID & Date Generation  
✅ Multi-Currency Support (USD, EUR, GBP, NGN, CAD, AUD)  
✅ Custom Branding (Logo Upload, Brand Color, Brand Name)  
✅ Bank Transfer Payment Details  
✅ Invoice Dashboard & Analytics  
✅ PDF Generation with WeasyPrint  
✅ PDF Download  
✅ Email Invoices (SMTP with PDF Attachment)  
✅ WhatsApp Share Links  
✅ Responsive Design  
✅ Complete Landing Page with Animations  
✅ All Marketing Pages (Features, Pricing, About, etc.)  
✅ FAQ, Support, Contact Pages  
✅ Terms, Privacy Policy Pages  
✅ Settings Page  
✅ PostgreSQL Database Support  
✅ Production-Ready Configuration  

## Render Free Tier Limitations

- **Web Service**: Spins down after 15 minutes of inactivity (cold starts)
- **Database**: 90-day expiration on free tier
- **Storage**: No persistent disk on free tier (use cloud storage for media)

## Upgrading to Paid Plan

For production use, consider upgrading:
- **Web Service**: $7/month (always on, no cold starts)
- **Database**: $7/month (persistent, no expiration)
- **Disk Storage**: $1/GB/month (for media files)

## Support

For issues or questions:
- GitHub Issues: [Your Repository URL]
- Email: support@smartinvoice.com
- Developer: [Jeffery Onome](https://onome-portfolio-ten.vercel.app/)

---

**Built with ❤️ by Jeffery Onome**
