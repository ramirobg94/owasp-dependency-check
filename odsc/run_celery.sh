#!/usr/bin/env bash

cd /app

# Load config
source config.sh

# Wait for database
sleep 4s

# Run Celery
gosu web /usr/local/bin/celery -A run:celery worker -l INFO