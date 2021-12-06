web: gunicorn base.wsgi --log-file - --bind 0.0.0.0:$PORT
heroku run python manage.py collectstatic --dry-run --noinput