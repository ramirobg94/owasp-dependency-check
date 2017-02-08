from flask import Blueprint, send_file, current_app


home_app = Blueprint("home_app", __name__)


@home_app.route("/", methods=["GET"])
def home():
    # return """
    # <html><head><title>Security Dependency Checker</title></head><body>
    # <h1>Wellcome to the Security Dependency Checker</h1>
    # <p>To access to interactive use of SDC API you can follow this link: <a
    # href="/apidocs/index.html">Access to API &rarr;</a></p>
    # </body></html>
    # """
    return send_file("{}/index.html".format(current_app.config["STATIC_DIR"]))

__all__ = ("home_app",)
