import os
import redis

from flask import Flask
from celery import Celery
from flask_cors import CORS
from flasgger import Swagger
from urllib.parse import urlparse
from pluginbase import PluginBase
from collections import defaultdict
from typing import Tuple, List, Dict, Union

from security_dependency_check import db, setup_db


def find_odsc_plugins(start_paths: List[str] = None) -> Union[Dict, object]:
    """
    Result format:
    {
        "nodejs": [
            ("function_name_1", function_object),
            ("function_name_2", function_object)
        ]
    }, Manager

    :param start_paths:
    :type start_paths:
    :return:
    :rtype:
    """
    start_paths = start_paths or [os.path.join(os.path.dirname(__file__),
                                               "plugins")]

    # Load plugins from directories
    # plugin_base = PluginBase(package=__package__)
    plugin_base = PluginBase(package="odsc.plugins")
    plugin_source = plugin_base.make_plugin_source(searchpath=start_paths)

    # Locate plugins
    plugins_found = defaultdict(list)

    for module in plugin_source.list_plugins():
        if module in ("core", "helpers", "web", "analyzers"):
            continue

        module_objects = plugin_source.load_plugin(module)

        for plugin_name, plugin_obj in vars(module_objects).items():
            if plugin_name.startswith("_") or \
                            type(plugin_obj).__name__ != "function":
                continue

            if hasattr(plugin_obj, "odsc_plugin_enable") and \
                    hasattr(plugin_obj, "odsc_plugin_lang"):
                for lang in plugin_obj.odsc_plugin_lang:
                    plugins_found[lang].append((plugin_name, module))

    return plugins_found, plugin_source


def make_celery(app: Flask) -> Celery:
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

    # Attach plugins
    plugins, manager = find_odsc_plugins()
    celery.ODSC_PLUGINS = plugins
    celery.ODSC_PLUGINS_MANAGER = manager

    app.config["CELERY"] = celery

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
    # celery = make_celery(app)
    # app.config["CELERY"] = celery

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
                "description": "Interactive API for the Security Dependency "
                               "Checker",
                "rule_filter": lambda rule: True  # all in
            }
        ]
    }
    Swagger(app)

    # Add CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # return app, celery
    return app


__all__ = ("make_app", "make_celery")
