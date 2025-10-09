#!/bin/bash

# Restaurant Menu System - Production Startup Script
# This script starts the production server with all necessary configurations

echo "🚀 Starting Restaurant Menu System in Production Mode"
echo "=================================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup first."
    exit 1
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Check if production settings exist
if [ ! -f "restaurant_api/settings_production.py" ]; then
    echo "❌ Production settings not found. Using development settings."
    SETTINGS_MODULE="restaurant_api.settings"
else
    echo "⚙️  Using production settings..."
    SETTINGS_MODULE="restaurant_api.settings_production"
fi

# Create logs directory if it doesn't exist
mkdir -p logs

# Check if database migrations are up to date
echo "🗄️  Checking database migrations..."
python manage.py showmigrations --settings=$SETTINGS_MODULE | grep -q "\[ \]"
if [ $? -eq 0 ]; then
    echo "⚠️  Unapplied migrations found. Running migrations..."
    python manage.py migrate --settings=$SETTINGS_MODULE
else
    echo "✅ Database migrations are up to date"
fi

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput --settings=$SETTINGS_MODULE

# Check if gunicorn is installed
if ! command -v gunicorn &> /dev/null; then
    echo "📦 Installing gunicorn..."
    pip install gunicorn
fi

# Start the production server
echo "🌐 Starting production server..."
echo "📍 Server will be available at: http://localhost:8000"
echo "🔐 Admin panel: http://localhost:8000/admin/"
echo "📊 API endpoints: http://localhost:8000/api/"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=================================================="

# Start gunicorn with production settings
gunicorn --config gunicorn.conf.py restaurant_api.wsgi:application
