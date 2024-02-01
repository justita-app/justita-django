#!/bin/sh

echo "--> Waiting for db to be ready"
./wait-for-it.sh db:5432

# Apply database migrations
echo "Apply database migrations"
python manage.py makemigration
python manage.py migrate

# Start server
echo "--> Starting web process"
gunicorn config.wsgi:application -b 0.0.0.0:8000