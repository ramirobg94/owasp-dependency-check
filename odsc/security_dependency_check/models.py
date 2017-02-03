import uuid

from sqlalchemy import CHAR
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_utils import database_exists, create_database


db = SQLAlchemy()


def make_uuid():
    return uuid.uuid4().hex


# --------------------------------------------------------------------------
# Models
# --------------------------------------------------------------------------
class Project(db.Model):
    id = db.Column(CHAR(32), primary_key=True, default=make_uuid)
    lang = db.Column(db.String(150))
    repo = db.Column(db.String(150))
    status = db.Column(db.String(150), default="created")
    total_tests = db.Column(db.Integer)
    passed_tests = db.Column(db.Integer, default=0)
    vulnerabilities = db.relationship('Vulnerabilities', backref="project",
                                      cascade="all, delete-orphan",
                                      lazy='dynamic')

    def __init__(self, lang, repo, total_tests):
        self.lang = lang
        self.repo = repo
        self.total_tests = total_tests

    def __repr__(self):
        return '<Project %r>' % self.repo


class Vulnerabilities(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product = db.Column(db.String(150))
    version = db.Column(db.String(100))
    severity = db.Column(db.String(20))
    description = db.Column(db.String(500))
    advisory = db.Column(db.String(500))
    project_id = db.Column(CHAR(32), db.ForeignKey('project.id'))

    def __init__(self, product,
                 version,
                 severity,
                 description,
                 advisory,
                 project_id):
        self.product = product
        self.version = version
        self.severity = severity
        self.description = description
        self.advisory = advisory
        self.project_id = project_id

    def __repr__(self):
        return '<product %r>' % self.product


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------
def setup_db(app):
    with app.app_context():
        engine = db.create_engine(app.config["SQLALCHEMY_DATABASE_URI"])

        # Check if database exits
        if not database_exists(engine.url):
            create_database(engine.url)

        # Create the scheme
        db.create_all()


__all__ = ("Project", "Vulnerabilities", "db", "setup_db")
