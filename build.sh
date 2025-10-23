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

echo "===== Build Process Complete ====="
echo "Note: Database migrations will run during pre-deploy phase"
