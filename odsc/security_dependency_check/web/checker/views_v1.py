import sqlalchemy

from flask import Blueprint, current_app, request, jsonify

from security_dependency_check import Project, celery, AVAILABLE_TASKS


checker_app = Blueprint("checker_app", __name__)


@checker_app.route("/api/v1/project/create", methods=["GET"])
def create():
    """
    This end point launch a new analysis and create a new project in the
    database.

    To launch a new project using command line, you can write:

        curl "http://mysite.com/api/v1/check?lang=nodejs&repo=https://github
        .com/ramirobg94/QuizCore"

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

    db = current_app.config["DB"]

    lang = request.args.get('lang', "nodejs")
    repo = request.args.get('repo', None)

    if not repo:
        return jsonify(error="Invalid repo value"), 400

    try:
        available_tasks = AVAILABLE_TASKS[lang]
    except KeyError:
        return jsonify(error="Language '{}' not available".format(lang)), 400

    # Store project information
    project = Project(lang, repo, len(available_tasks))
    db.session.add(project)
    db.session.commit()

    celery.send_task("core_dispatch", args=(lang, repo, project.id))

    return jsonify(project=project.id)


@checker_app.route("/api/v1/project/status/<int:project_id>", methods=["GET"])
def status(project_id):
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
        project = Project.query.filter_by(id=project_id).one()
    except sqlalchemy.orm.exc.NoResultFound:
        return jsonify(error='Project ID not found'), 404

    ret = dict(
        scan_status=project.status,
        total_tests=project.total_tests,
        passed_tests=project.passed_tests
    )

    return jsonify(ret)


@checker_app.route("/api/v1/project/results/<int:project_id>", methods=["GET"])
def results(project_id):
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
    VALUES_TO_HIDE_PROJECT = ("id", "total_tests")
    VALUES_TO_HIDE_VULNS = ("id", "project_id")

    try:
        project = Project.query.filter_by(id=project_id).one()
    except sqlalchemy.orm.exc.NoResultFound:
        return jsonify(error='Project ID not found'), 404

    # Load project info
    project_info = {
        x: y for x, y in project.__dict__.items()
        if not x.startswith("_") and x not in VALUES_TO_HIDE_PROJECT
        }

    # Load vulns
    vulnerabilities = [
        {y: z for y, z in x.__dict__.items() if not y.startswith("_") and \
         y not in VALUES_TO_HIDE_VULNS}
        for x in project.vulnerabilities.all()
        ]

    return jsonify(dict(
        project_info=project_info,
        vulnerabilities=vulnerabilities
    ))


__all__ = ("checker_app",)
