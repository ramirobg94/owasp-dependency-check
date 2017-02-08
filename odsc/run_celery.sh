#!/usr/bin/env bash

# Load config
source /odsc/config.sh

# Wait for database
sleep 4s

# Run Celery
/usr/local/bin/celery -A run:celery worker -l INFO