from flask import Blueprint, jsonify

from security_dependency_check import AVAILABLE_TASKS

miscellaneous_app = Blueprint("miscellaneous", __name__)


@miscellaneous_app.route("/api/v1/languages", methods=["GET"])
def available_languages():
    """
    Get all supported languages
    ---
    tags:
      - Miscellaneous
    responses:
        200:
            description: Get supported languages
            schema:
                id: get_supported_languages
                properties:
                    languages:
                      type: list
                        - running
            examples:
                application/json:
                    languages:
                    - nodejs
    """
    return jsonify(dict(languages=[x for x in AVAILABLE_TASKS.keys()]))


__all__ = ("miscellaneous_app", )
