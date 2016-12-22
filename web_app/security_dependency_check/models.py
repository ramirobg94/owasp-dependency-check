from flask import current_app
from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()


# --------------------------------------------------------------------------
# Models
# --------------------------------------------------------------------------
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lang = db.Column(db.String(150))
    repo = db.Column(db.String(150))
    type = db.Column(db.String(150))
    numberTests = db.Column(db.Integer)
    passedTests = db.Column(db.Integer)
    vulnerabilities = db.relationship('Vulnerabilities', backref="project", cascade="all, delete-orphan", lazy='dynamic')
    
    def __init__(self, lang, repo, type, numberTests, passedTests):
        self.lang = lang
        self.repo = repo
        self.type = type
        self.numberTests = numberTests
        self.passedTests = passedTests
    
    def __repr__(self):
        return '<repo %r>' % self.repo


class Vulnerabilities(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product = db.Column(db.String(150))
    version = db.Column(db.String(100))
    severity = db.Column(db.String(20))
    description = db.Column(db.String(500))
    advisory = db.Column(db.String(500))
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    
    def __init__(self, product, version, severity, description, advisory, project_id):
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
    
    # Create all tables
    with app.app_context():
        db.create_all()

__all__ = ("Project", "Vulnerabilities")
