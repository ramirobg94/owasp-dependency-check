import pytest

from odsc.run import app as app_instance


@pytest.fixture
def app():
    # app_instance, celery = make_app("config.py")
    return app_instance
