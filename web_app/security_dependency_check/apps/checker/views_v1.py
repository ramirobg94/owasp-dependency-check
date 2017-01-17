from flask import Blueprint, current_app, request

from security_dependency_check import Project, celery


checker_app = Blueprint("checker_app", __name__)


@checker_app.route("/api/v1/", methods=["GET"])
def home():
    celery.send_task("mytask", args=(2, 3))

    return "hola"


@checker_app.route("/api/v1/check", methods=["POST", "GET"])
def check():
    """
    Check a project. To test:
     
    host/check?lang=java&repo=git@github.com:ramirobg94/QuizCore.git&type=git
    
    http://myservice.com/api/v1/check
    
    """
    db = current_app.config["DB"]
    
    lang = request.args.get('lang', "nodejs")
    repo = request.args.get('repo', None)
    type = request.args.get('type', "git")  # zip or git

    project = Project(lang, repo, type, 2, 0)
    
    db.session.add(project)
    db.session.commit()
    
    celery.send_task("owasp_dependency_checker_task", args=(lang, repo, type, project.id))
    celery.send_task("retire_task", args=(lang, repo, type, project.id))

    return "checking project {} you can check the status at: /status/{}".format(str(project.id), str(project.id))


@checker_app.route("/api/v1/status/<int:project_id>", methods=["GET"])
def status(project_id):
    """Check the state and vulnerability of the project"""
    project = Project.query.filter_by(id=project_id).one()
    #vuls = Vulnerabilities.query.filter_by(project_id = project_id)
    #vuls = project.vulnerabilities

    status = project.numberTests - project.passedTests
    if status == 0:
        return 'finish'
    else:
        return 'running'


__all__ = ("checker_app", )
