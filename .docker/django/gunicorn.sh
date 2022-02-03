#!/bin/sh
python /app/manage.py collectstatic --noinput
gunicorn config.wsgi -w 4 -t 60 -b 0.0.0.0:5000 --chdir=/app
