#!/usr/bin/env bash
# exit on error
set -o errexit

# Install Node.js dependencies and build Tailwind CSS
npm install
npm run build:css

# Install Python dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Run database migrations
python manage.py migrate
