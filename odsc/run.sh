#!/usr/bin/env bash

#!/usr/bin/env bash

if [ -z "$REDIS_HOST" ]; then
    SDC_REDIS="redis://$REDIS_HOST:$REDIS_PORT"
    SDC_CELERY_BACKEND="redis://$REDIS_HOST:$REDIS_PORT"
    SDC_CELERY_BROKER_URL="redis://$REDIS_HOST:$REDIS_PORT"
fi

if [ -z "$POSTGRES_HOST" ]; then
    POSTGRES_HOST="postgresql+psycopg2://$POSTGRES_USER:$POSTGRES_PASSWORD@$POSTGRES_HOST/$POSTGRES_DB"
fi

cd /app

# Run Celery
gosu web /usr/local/bin/celery -A run:celery worker -l INFO

# Run the web
gosu web /usr/local/bin/gunicorn \
            --error-logfile /logs/error.log \
            --access-logfile /logs/access.log \
            -w $WORKERS \
            run:app -b $LISTEN_ADDR:$LISTEN_PORT