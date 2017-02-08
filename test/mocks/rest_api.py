"""
This file contains an REST API that simulates the real backend but all actions
are mocked
"""

import uuid
import random

from flasgger import Swagger
from flask import Flask, request, jsonify

mock_rest_api = Flask("rest_mock")

Swagger(mock_rest_api)

ODSC_PLUGINS = {
    'nodejs': 2
}

PROJECT_LIST = {}
PROJECT_STATUS = {}
PROJECT_RESULTS = {}


def _update_project(project_id):
    if PROJECT_STATUS[project_id] > 0:
        PROJECT_STATUS[project_id] -= 1

    if PROJECT_STATUS[project_id] == 0:
        PROJECT_LIST[project_id]["status"] = "finished"
        PROJECT_LIST[project_id]["passed_tests"] = \
            PROJECT_LIST[project_id]["total_tests"]

        PROJECT_RESULTS[project_id] = [
            {
                "advisory": "CVE-2015-6607",
                "description": "SQLite before 3.8.9, as used in Android "
                               "before 5.1.1 LMY48T, allows attackers to "
                               "gain privileges via a crafted "
                               "application, aka internal bug 20099586.",
                "product": "sqlite",
                "severity": "Low",
                "version": "3.8.8.3"
            },
            {
                "advisory": "CVE-2015-3717",
                "description": "Multiple buffer overflows in the printf "
                               "functionality in SQLite, as used in "
                               "Apple iOS before 8.4 and OS X before "
                               "10.10.4, allow remote attackers to "
                               "execute arbitrary code or cause a denial "
                               "of service (application crash) via "
                               "unspecified vectors.",
                "product": "mac_os_x",
                "severity": "High",
                "version": "10.10.3"
            },
            {
                "advisory": "CVE-2015-3717",
                "description": "Multiple buffer overflows in the printf "
                               "functionality in SQLite, as used in "
                               "Apple iOS before 8.4 and OS X before "
                               "10.10.4, allow remote attackers to "
                               "execute arbitrary code or cause a denial "
                               "of service (application crash) via "
                               "unspecified vectors.",
                "product": "mac_os_x",
                "severity": "High",
                "version": "10.10.3"
            },
            {
                "advisory": "CVE-2015-3717",
                "description": "Multiple buffer overflows in the printf "
                               "functionality in SQLite, as used in "
                               "Apple iOS before 8.4 and OS X before "
                               "10.10.4, allow remote attackers to "
                               "execute arbitrary code or cause a denial "
                               "of service (application crash) via "
                               "unspecified vectors.",
                "product": "mac_os_x",
                "severity": "Medium",
                "version": "10.10.3"
            },
            {
                "advisory": "CVE-2015-3717",
                "description": "Multiple buffer overflows in the printf "
                               "functionality in SQLite, as used in "
                               "Apple iOS before 8.4 and OS X before "
                               "10.10.4, allow remote attackers to "
                               "execute arbitrary code or cause a denial "
                               "of service (application crash) via "
                               "unspecified vectors.",
                "product": "mac_os_x",
                "severity": "High",
                "version": "10.10.3"
            }
        ]


@mock_rest_api.route("/api/v1/projects", methods=["GET"])
def projects_summary():
    pass


@mock_rest_api.route("/api/v1/projects", methods=["POST"])
def create():
    """
    This end point launch a new analysis and create a new project in the
    database.

    To launch a new project using command line, you can write:

        curl "http://mysite.com/api/v1/check?lang=nodejs&repo=https://github
        .com/ramirobg94/QuizCore"

    Repo example:

    https://github.com/ramirobg94/QuizCore

    ---
    tags:
      - Analysis
    parameters:
      - name: lang
        in: query
        description: >
            The language or project code. i.e: nodejs, java, python...
        required: true
        type: string
        default: nodejs
        enum:
            - nodejs
      - name: repo
        in: query
        description: >
            Remote repository address. i.e:
            https://github.com/ramirobg94/QuizCore
        required: true
        type: string
    responses:
        200:
            description: Analysis launched correctly
            schema:
                id: create_analysis_ok
                properties:
                    project:
                      type: int
                      required: true
                      description: return the project ID
            examples:
                application/json:
                    project: 20
        400:
            schema:
                id: create_analysis_invalid_input
                properties:
                    error:
                      type: string
                      description: error message
    """

    lang = request.args.get('lang', "nodejs")
    repo = request.args.get('repo', None)

    if not repo:
        return jsonify(error="Invalid repo value"), 400

    try:
        available_tasks = ODSC_PLUGINS[lang]
    except KeyError:
        return jsonify(error="Language '{}' not available".format(lang)), 400

    project_id = uuid.uuid4().hex

    # Generate Project
    PROJECT_LIST[project_id] = dict(repo=repo,
                                    lang=lang,
                                    status="created",
                                    total_tests=available_tasks,
                                    passed_tests=0)
    PROJECT_STATUS[project_id] = random.randint(1, 10)
    PROJECT_RESULTS[project_id] = []

    return jsonify(project=project_id)


@mock_rest_api.route("/api/v1/projects/<string:project_id>", methods=["GET"])
def project_summary(project_id):
    pass


@mock_rest_api.route("/api/v1/projects/<string:project_id>/revisions",
                     methods=["GET"],
                     defaults={"revision_id": 0})
@mock_rest_api.route("/api/v1/projects/<string:project_id>/revisions/<int:revision_id>",
                     methods=["GET"])
def revisions(project_id, revision_id=0):
    pass


@mock_rest_api.route("/api/v1/projects/<string:project_id>/status",
                     methods=["GET"],
                     defaults={"revision_id": 0})
@mock_rest_api.route("/api/v1/projects/<string:project_id>/status/<int:revision_id>",
                     methods=["GET"])
def status(project_id, revision_id=None):
    """
    Check and return the state and vulnerability of the project

    ---
    tags:
      - Analysis
    parameters:
      - name: project_id
        in: path
        description: >
            The project ID to check state
        required: true
        type: string
    responses:
        200:
            description: The current status of the analysis
            schema:
                id: check_project_status_project_check
                properties:
                    scan_status:
                      type: string
                      required: true
                      description: return the project status
                      enum:
                        - created
                        - finished
                        - running
                        - non-accessible
                    total_tests:
                      type: int
                      required: true
                      description: return total test that will be passed
                    passed_tests:
                      type: int
                      required: true
                      description: return finished test at the moment ot check
            examples:
                application/json:
                    project: "finish"
                    total_tests: 2
                    passed_tests: 2
                application/json:
                    project: "running"
                    total_tests: 2
                    passed_tests: 1
        404:
            schema:
                id: check_project_status_project_not_found
                properties:
                    error:
                      type: string
                      description: error message
    """

    try:
        _update_project(project_id)

        return jsonify(PROJECT_LIST[project_id])
    except KeyError:
        return jsonify(error='Project ID not found'), 404


@mock_rest_api.route("/api/v1/results/<string:project_id>/<int:revision_id>", methods=["GET"])
def results(project_id, revision_id=0):
    """
    Return the results for a project

    ---
    tags:
      - Analysis
    parameters:
      - name: project_id
        in: path
        description: >
            The project ID to get results
        required: true
        type: string
    responses:
        200:
            description: results returned
            schema:
                id: project_results_ok
                properties:
                    project_info:
                      type: list
                    vulnerabilities:
                      type: list

            examples:
                application/json:
                    project_info:
                        lang: "nodejs"
                        passedTest: 1
                        repo: "https://github.com/ramirobg94/QuizCore"
                        scan_status: "finished"
                        type: "git"
                    vulnerabilities:
                        - { version: 3.8.8.3, product: sqlite, severity:
                        Medium, advisory: CVE-2015-6607, description:
                        "SQLite before 3.8.9, as used in Android before
                        5.1.1 LMY48T, allows attackers to gain privileges
                        via a crafted application, aka internal bug 20099586."}
                        - { version: 10.10.3, product: mac_os_x, severity:
                        High, advisory: CVE-2015-3717, description:
                        "Multiple buffer overflows in the printf
                        functionality in SQLite, as used in Apple iOS before
                        8.4 and OS X before 10.10.4, allow remote attackers
                        to execute arbitrary code or cause a denial of
                        service (application crash) via unspecified vectors."}

        404:
            schema:
                id: project_results_not_found
                properties:
                    error:
                      type: string
                      description: error message
    """

    _update_project(project_id)

    try:
        return jsonify({
            "project_info": PROJECT_LIST[project_id],
            "vulnerabilities": PROJECT_RESULTS[project_id]
        })

    except KeyError:
        return jsonify(error='Project ID not found'), 404

#
#
#
#

if __name__ == '__main__':
    mock_rest_api.run("127.0.0.1",
                      port=8000)
