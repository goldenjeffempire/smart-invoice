#!/usr/bin/env bash
# exit on error
set -o errexit

echo "===== Starting Build Process ====="

# Install Node.js dependencies and build Tailwind CSS
echo "Installing Node.js dependencies (including devDependencies for TailwindCSS)..."
npm ci

echo "Building Tailwind CSS..."
npm run build:css

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --no-input --clear

# Run database migrations
echo "Running database migrations..."
python manage.py migrate --no-input

# Create cache table for production
echo "Creating cache table..."
python manage.py createcachetable || echo "Cache table may already exist"

echo "===== Build Process Complete ====="
