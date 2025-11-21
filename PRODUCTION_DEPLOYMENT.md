# Smart Invoice - Production Deployment Guide

## Deployment Checklist

### Pre-Deployment
- [ ] Set `DEBUG=False` in environment
- [ ] Generate secure `SECRET_KEY` 
- [ ] Set `ALLOWED_HOSTS` to your domain(s)
- [ ] Configure `DATABASE_URL` for PostgreSQL
- [ ] Set up email configuration (SMTP credentials)
- [ ] Run `python manage.py migrate` on production database
- [ ] Run `python manage.py collectstatic --noinput`
- [ ] Test locally with DEBUG=False

### Render.com Deployment

**1. Create New Web Service**
- Connect your GitHub repository
- Environment: Python
- Build Command: 
  ```
  pip install -r requirements.txt && npm run build:css && python manage.py migrate && python manage.py collectstatic --noinput
  ```
- Start Command: 
  ```
  gunicorn smart_invoice.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --threads 4
  ```

**2. Environment Variables**
```
DEBUG=False
SECRET_KEY=<generate-secure-key>
ALLOWED_HOSTS=your-domain.onrender.com
DATABASE_URL=<your-postgres-url>
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=<your-email@gmail.com>
EMAIL_HOST_PASSWORD=<your-app-password>
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
CSRF_TRUSTED_ORIGINS=https://*.onrender.com,https://your-domain.com
```

**3. Create PostgreSQL Database**
- Add PostgreSQL instance on Render
- Copy connection string to `DATABASE_URL`

**4. Deploy**
- Push to main/master branch
- Render will auto-deploy

### Heroku Deployment

```bash
# Install Heroku CLI
curl https://cli-assets.heroku.com/install.sh | sh

# Login
heroku login

# Create app
heroku create your-app-name

# Add PostgreSQL
heroku addons:create heroku-postgresql:standard-0

# Set environment variables
heroku config:set DEBUG=False
heroku config:set SECRET_KEY=$(python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
heroku config:set ALLOWED_HOSTS=your-app-name.herokuapp.com
# ... set other variables

# Deploy
git push heroku main

# Run migrations
heroku run python manage.py migrate

# Create superuser
heroku run python manage.py createsuperuser
```

### Production Security Settings

The platform includes automatic production hardening:

**Auto-Applied in Production (DEBUG=False, not Replit):**
- ✅ SECURE_SSL_REDIRECT = True (force HTTPS)
- ✅ SESSION_COOKIE_SECURE = True (secure cookies only)
- ✅ CSRF_COOKIE_SECURE = True (secure CSRF tokens)
- ✅ SECURE_HSTS_SECONDS = 31536000 (1 year HSTS)
- ✅ SECURE_HSTS_INCLUDE_SUBDOMAINS = True
- ✅ SECURE_HSTS_PRELOAD = True

### Database Migrations

```bash
# Remote migration
heroku run python manage.py migrate
# OR on Render
render exec <service-name> python manage.py migrate
```

### Monitoring & Logs

**Render:**
```bash
# View logs
render logs <service-name>

# Follow logs
render logs <service-name> --follow
```

**Heroku:**
```bash
# View logs
heroku logs --tail

# View specific app logs
heroku logs --app your-app-name --tail
```

### Custom Domain

**Render:**
1. Go to Settings → Domains
2. Add custom domain
3. Update DNS records per instructions

**Heroku:**
1. Purchase domain
2. Add domain to app: `heroku domains:add yourdomain.com`
3. Update DNS to Heroku nameservers

### Backup & Disaster Recovery

**PostgreSQL Backups on Render:**
- Automated daily backups included
- Manual backup: `render exec <service> pg_dump ...`

**Heroku Backups:**
- `heroku pg:backups:capture`
- `heroku pg:backups:download`

### Performance Optimization

**Already Included:**
- ✅ Database indexes on frequently queried fields
- ✅ WhiteNoise static file serving
- ✅ Gunicorn with worker pool optimization
- ✅ CSS minification (36KB Tailwind output)
- ✅ Lazy loading for images
- ✅ Query optimization with select_related

**Additional Recommendations:**
- Enable CDN (Cloudflare) for static assets
- Use Redis for caching (optional)
- Enable gzip compression
- Monitor with Sentry for error tracking

### Troubleshooting

**500 Error on Deploy:**
```bash
# Check logs
render logs <service-name> -n 100

# Check migrations
render exec <service-name> python manage.py showmigrations
```

**Database Connection Error:**
- Verify DATABASE_URL is correct
- Check PostgreSQL is running
- Verify network access if using external DB

**Static Files Not Loading:**
- Run `python manage.py collectstatic --noinput`
- Check STATIC_ROOT and STATIC_URL settings
- Verify WhiteNoise is configured

**Email Not Sending:**
- Verify EMAIL_HOST and SMTP credentials
- Check email provider's app password settings
- Enable "Less secure apps" if using Gmail

### Scale Up

**Heroku Pro tier:**
- More dyno types (Premium-1X, Premium-2X)
- Better performance
- More reliable

**Render Paid tier:**
- Auto-scaling options
- More powerful compute
- Priority support

---

**Questions?** Check AUDIT_REPORT.md for complete feature documentation.
