"""
Settings module selector for Smart Invoice.
Automatically loads the correct settings based on DJANGO_ENV environment variable.
"""
import os

# Determine which settings to use based on environment
env = os.environ.get('DJANGO_ENV', 'development')

if env == 'production':
    from .prod import *
else:
    from .dev import *
