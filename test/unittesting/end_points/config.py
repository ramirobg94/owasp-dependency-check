import os

REDIS = os.environ.get("SDC_REDIS", "redis://localhost:6379")

# --------------------------------------------------------------------------
# Config celery
# --------------------------------------------------------------------------
CELERY_BACKEND = os.environ.get("SDC_CELERY_BACKEND", "redis://localhost:6379")
CELERY_BROKER_URL = os.environ.get("SDC_CELERY_BROKER_URL",
                                   "redis://localhost:6379")

# --------------------------------------------------------------------------
# Config database
# --------------------------------------------------------------------------
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_DATABASE_URI = os.environ.get(
    "SDC_DATABASE_DSN",
    "postgresql+pg8000://postgres:password@localhost/vulnerabilities")

ADDITIONAL_BINARY_PATHS = os.environ.get("SDC_ADDITIONAL_PATHS", ":/usr/local/bin/")