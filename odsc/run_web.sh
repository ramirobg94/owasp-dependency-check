#!/usr/bin/env bash

# Load config
source /odsc/config.sh

# Wait for database
sleep 4s

echo $ODSC_LISTEN_ADDR:$ODSC_LISTEN_PORT

# Run the web
#/usr/local/bin/python run.py
/usr/local/bin/gunicorn \
            --error-logfile /logs/error.log \
            --access-logfile /logs/access.log \
            -w $ODSC_WORKERS \
            run:app -b $ODSC_LISTEN_ADDR:$ODSC_LISTEN_PORT