#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install Python dependencies
pip install -r requirements.txt

# Run Tailwind CSS build
# If you are using django-tailwind:
python manage.py tailwind build
# If you are using a manual Tailwind CLI setup:
# npm install
# npx tailwindcss -i ./static/src/input.css -o ./static/dist/output.css --minify

# Collect static files (Django)
python manage.py collectstatic --no-input

# Apply database migrations
python manage.py migrate

# (Optional) Create a superuser if it doesn't exist
# python manage.py createsuperuser --no-input || true