echo "Running Django Migrations"
uv run python manage.py migrate

echo "Running Django Collectstatic"
uv run python manage.py collectstatic --noinput

uv run gunicorn --bind=0.0.0.0:8000 website.wsgi

