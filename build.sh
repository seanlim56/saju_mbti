#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

# Remove old database to avoid migration conflicts
rm -f db.sqlite3

python manage.py collectstatic --no-input
python manage.py makemigrations --noinput
python manage.py migrate --noinput
