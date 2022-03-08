#!/usr/bin/env bash
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ] ; then
    (cd rekome; python manage.py createsuperuser --no-input)
fi
(cd rekome; python manage.py collectstatic --noinput; gunicorn rekome.wsgi --user www-data --bind 0.0.0.0:8010 --workers 3) &
nginx -g "daemon off;"
