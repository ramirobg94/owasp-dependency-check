import redis

from flask import Flask
from typing import Tuple
from celery import Celery
from flasgger import Swagger
from urllib.parse import urlparse

from security_dependency_check import db, setup_db


def _make_celery(app: Flask) -> Celery:
    celery = Celery(app.import_name,
                    backend=app.config.get('CELERY_BACKEND'),
                    broker=app.config.get('CELERY_BROKER_URL'))
    celery.conf.update(app.config)

    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask

    return celery


def _setup_redis(config: dict) -> redis.StrictRedis:
    _, netloc, path, _, _, _ = urlparse(config["REDIS"])

    host, port = netloc.split(":", maxsplit=1)

    if not path:
        path = 0

    redis_db = redis.StrictRedis(host=host,
                                 port=port,
                                 db=path)

    return redis_db


def make_app(config_path: str) -> Tuple[Flask, Celery]:

    # Create the app
    app = Flask(__name__)

    # Load config
    app.config.from_pyfile(config_path)

    # Config the broker
    app.config["REDIS"] = _setup_redis(app.config)

    # Init database handler
    db.init_app(app)
    setup_db(app)

    # Config celery
    celery = _make_celery(app)
    app.config["CELERY"] = celery

    # Store SQL Alchemy
    app.config["DB"] = db

    # Swagger config
    app.config['SWAGGER'] = {
        # "swagger_version": "2.0",
        "specs": [
            {
                "version": "0.8.0",
                "title": "SDC API - v1",
                "endpoint": 'spec',
                "route": '/spec',
                "description": "Interactive API for the Security Dependency Checker",
                "rule_filter": lambda rule: True  # all in
            }
        ]
    }
    Swagger(app)

    return app, celery


__all__ = ("make_app", )
