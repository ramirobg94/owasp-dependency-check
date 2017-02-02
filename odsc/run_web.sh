#!/usr/bin/env bash

cd /app

# Load config
source config.sh

# Wait for database
sleep 4s

# Run the web
gosu web /usr/local/bin/python run.py
            --error-logfile /logs/error.log \
            --access-logfile /logs/access.log \
            -w $ODSC_WORKERS \
            run:app -b $ODSC_LISTEN_ADDR:$ODSC_LISTEN_PORT