#!/usr/bin/env bash

#
# Ensure Redis config
#
if [ -z "$ODSC_REDIS_HOST" ]; then
    ODSC_REDIS_HOST="127.0.0.1"
fi

if [ -z "$REDIS_PORT" ]; then
    ODSC_REDIS_PORT=6379
fi

#
# Ensure Postgres config
#
if [ -z "$ODSC_POSTGRES_HOST" ]; then
    ODSC_POSTGRES_HOST="127.0.0.1"
fi

if [ -z "$ODSC_POSTGRES_PORT" ]; then
    ODSC_POSTGRES_PORT="5432"
fi

if [ -z "$ODSC_POSTGRES_PASSWORD" ]; then
    ODSC_POSTGRES_PASSWORD="postgres"
fi

if [ -z "$ODSC_POSTGRES_USER" ]; then
    ODSC_POSTGRES_USER="postgres"
fi

if [ -z "$ODSC_POSTGRES_DB" ]; then
    ODSC_POSTGRES_DB="vulnerabilities"
fi

#
# Ensure running config
#
if [ -z "$ODSC_WORKERS" ]; then
   export ODSC_WORKERS=4
fi

if [ -z "$ODSC_LISTEN_ADDR" ]; then
    export ODSC_LISTEN_ADDR=127.0.0.1
fi

if [ -z "$ODSC_LISTEN_PORT" ]; then
    export ODSC_LISTEN_PORT=8000
fi

#
# Build config
#
export ODSC_REDIS="redis://$ODSC_REDIS_HOST:$ODSC_REDIS_PORT"
export ODSC_CELERY_BACKEND="redis://$ODSC_REDIS_HOST:$ODSC_REDIS_PORT"
export ODSC_CELERY_BROKER_URL="redis://$ODSC_REDIS_HOST:$ODSC_REDIS_PORT"
export ODSC_DATABASE_DSN="postgresql+psycopg2://$ODSC_POSTGRES_USER:$ODSC_POSTGRES_PASSWORD@$ODSC_POSTGRES_HOST:$ODSC_POSTGRES_PORT/$ODSC_POSTGRES_DB"