import os

REDIS = os.environ.get("ODSC_REDIS", "redis://localhost:6379")

# --------------------------------------------------------------------------
# Config celery
# --------------------------------------------------------------------------
CELERY_BACKEND = os.environ.get("ODSC_CELERY_BACKEND", "redis://localhost:6379")
CELERY_BROKER_URL = os.environ.get("ODSC_CELERY_BROKER_URL",
                                   "redis://localhost:6379")

# --------------------------------------------------------------------------
# Config database
# --------------------------------------------------------------------------
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_DATABASE_URI = os.environ.get(
    "ODSC_DATABASE_DSN",
    "postgresql+psycopg2://postgres:password@localhost/vulnerabilities")

ADDITIONAL_BINARY_PATHS = os.environ.get("ODSC_ADDITIONAL_PATHS",
                                         ":/usr/local/bin/")


STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")