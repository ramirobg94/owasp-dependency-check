#!/usr/bin/env bash

# Launch site
gosu web /usr/local/bin/gunicorn \
            --error-logfile /logs/error.log \
            --access-logfile /logs/access.log \
            -w $WORKERS \
            mlwr_core.wsgi:application -b 0.0.0.0:8000