#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

# Build Tailwind CSS if the compiled file doesn't exist
TAILWIND_OUT="theme/static/css/dist/styles.css"
if [ ! -f "$TAILWIND_OUT" ]; then
    echo "Tailwind CSS not found, building..."
    cd theme/static_src
    npm install
    npm run build
    cd ../..
else
    echo "Tailwind CSS already built, skipping."
fi

python manage.py collectstatic --no-input
python manage.py migrate

# Automatically create a superuser for Render free tier
python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'phonemarketplace.settings')
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    # Provide phone as it's a field in CustomUser
    User.objects.create_superuser('admin', 'admin@example.com', 'Admin@1234', phone='0000000000')
    print('Superuser created successfully: admin / Admin@1234')
else:
    print('Superuser already exists.')
"
