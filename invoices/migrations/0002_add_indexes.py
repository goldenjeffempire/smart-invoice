# Generated migration for adding database indexes for performance optimization

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoices', '0001_initial'),
    ]

    operations = [
        # Add index on user + status for faster dashboard queries
        migrations.AddIndex(
            model_name='invoice',
            index=models.Index(fields=['user', 'status'], name='invoice_user_status_idx'),
        ),
        # Add index on user + created_at for analytics queries
        migrations.AddIndex(
            model_name='invoice',
            index=models.Index(fields=['user', '-created_at'], name='invoice_user_created_idx'),
        ),
        # Add index on user + invoice_date for filtering
        migrations.AddIndex(
            model_name='invoice',
            index=models.Index(fields=['user', 'invoice_date'], name='invoice_user_date_idx'),
        ),
        # Add index on invoice_id for faster lookups
        migrations.AddIndex(
            model_name='invoice',
            index=models.Index(fields=['invoice_id'], name='invoice_id_idx'),
        ),
        # Add index on client_email for analytics
        migrations.AddIndex(
            model_name='invoice',
            index=models.Index(fields=['user', 'client_email'], name='invoice_user_client_idx'),
        ),
    ]
