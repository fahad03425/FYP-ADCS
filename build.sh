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
