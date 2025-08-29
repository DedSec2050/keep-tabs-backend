#!/bin/bash

# Exit on error
set -e

# Check if environment argument is provided
if [ -z "$1" ]; then
    echo "Usage: ./migrate_and_run.sh [dev|prod]"
    exit 1
fi

ENVIRONMENT=$1

# Map environment to settings module
if [ "$ENVIRONMENT" == "dev" ]; then
    SETTINGS_MODULE="core.settings.dev"
elif [ "$ENVIRONMENT" == "prod" ]; then
    SETTINGS_MODULE="core.settings.prod"
else
    echo "Invalid environment: $ENVIRONMENT"
    echo "Valid options: dev, prod"
    exit 1
fi

echo "🚀 Starting migration + server for $ENVIRONMENT environment..."

# Run migrations
python manage.py makemigrations --settings=$SETTINGS_MODULE
python manage.py migrate --settings=$SETTINGS_MODULE

# Run server based on environment
if [ "$ENVIRONMENT" == "dev" ]; then
    echo "🔧 Development server starting..."
    python manage.py runserver 0.0.0.0:8000 --settings=$SETTINGS_MODULE
elif [ "$ENVIRONMENT" == "prod" ]; then
    echo "📦 Collecting static files..."
    python manage.py collectstatic --noinput --settings=$SETTINGS_MODULE
    
    echo "🛠 Starting Gunicorn..."
    gunicorn core.wsgi:application \
        --bind 0.0.0.0:8000 \
        --workers 3 \
        --env DJANGO_SETTINGS_MODULE=$SETTINGS_MODULE
fi
