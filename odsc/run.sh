#!/usr/bin/env bash

cd /app

# Run Celery
gosu web /usr/local/bin/celery -A run:celery worker -l FATAL &

# Run the web
gosu web /usr/local/bin/gunicorn \
            --error-logfile /logs/error.log \
            --access-logfile /logs/access.log \
            -w $WORKERS \
            run:app -b 0.0.0.0:8000