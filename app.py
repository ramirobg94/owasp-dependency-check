from flask import Flask
from flask import request
from celery import Celery
from cpe import CPE
import os
from subprocess import call
import time
from vulnerability import Vulnerability
import xml.etree.ElementTree as ET
from flask_sqlalchemy import SQLAlchemy
import redis



def make_celery(app):
    celery = Celery(app.import_name, backend=app.config['CELERY_BACKEND'],
                    broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task
    
    class ContextTask(TaskBase):
        abstract = True
        
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    
    celery.Task = ContextTask
    return celery

app = Flask('checker')
app.config.update(
    CELERY_BACKEND='redis://localhost:6379',
    CELERY_BROKER_URL='redis://localhost:6379'
)

redis_db = redis.StrictRedis(host="localhost", port=6379, db=0)
redis_db.ping

celery = make_celery(app)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+pg8000://postgres:password@localhost/vulnerabilities'
db = SQLAlchemy(app)

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


@celery.task(name="mytask")
def add(x, y):
    print(x)
    return x + y

@celery.task(name="joinertask")
def joinertask(project_id, other):

    p = Project.query.get(project_id)
    p.passedTests  = p.passedTests + 1
    db.session.commit()
    if (p.passedTests == p.numberTests):
        r = redis_db.hgetall(project_id)
        print(project_id)
        results = []
        for x in r.values():
            results.append(eval(x.decode()))

        cleaned_results = []

        #print(results)
        print(len(results))
        for i, result in enumerate(results):

            if( result['library'] == ''):
                pass
            elif (len(cleaned_results) <= 0):
                cleaned_results.append(result)
            else:
                _temp_add = {}
                for vulR in cleaned_results:
                    if(result['library'] == vulR['library'] and result['advisory'] == vulR['advisory']):
                        break
                else:
                    _temp_add = result

                if (len(_temp_add) > 0):
                    cleaned_results.append(_temp_add)


        #print(cleaned_results)
        print(len(cleaned_results))
        for vul in cleaned_results:
            vul = Vulnerabilities(vul['library'], vul['version'], vul['severity'],vul['summary'], vul['advisory'], project_id)
            db.session.add(vul)
            db.session.commit()

        vuls = Vulnerabilities.query.all()
        #print(vuls)


    return "joiner TODO"


@celery.task(name="checkertask")
def checkertask(lang, repo, type, project_id):

    path = repo.split('/')[-1]
    name = path[:-4]
    path = '/tmp/repoTmpo/' + name
    os.system('git clone '+repo+' '+path)
    os.system('dependency-check --project "'+ repo +'"  --scan "'+ path +'" -f "XML" -o  "'+ path +'" --enableExperimental')

    tree = ET.parse(path + '/dependency-check-report.xml')
    root = tree.getroot()
    cleared_results = []
    for neighbor in root[2]:
        for elemts in neighbor:
            if 'vulnerabilities' in elemts.tag:
                for vulnerability in elemts:
                    for vulnerabilityTags in vulnerability:

                        if 'severity' in vulnerabilityTags.tag:
                            severity = vulnerabilityTags.text
                        if 'description' in vulnerabilityTags.tag:
                            description =  vulnerabilityTags.text
                        if 'name' in vulnerabilityTags.tag:
                            advisor = vulnerabilityTags.text
                        if 'vulnerableSoftware' in vulnerabilityTags.tag:
                            for software in vulnerabilityTags:
                                if 'allPreviousVersion' in software.attrib:
                                    cpe = CPE(software.text)
                                    product = cpe.get_product()[0]
                                    version = cpe.get_version()[0]
                                    vulnerability = Vulnerability(product, version, severity, description, advisor)
                                    redis_db.hmset(project_id, {'%s' % id(vulnerability): vulnerability.__dict__})
                                    #cleared_results.append(vulnerability)


    #for vulnerability in cleared_results:
    #    vul  = Vulnerabilities(vulnerability.library, vulnerability.version, vulnerability.severity, vulnerability.summary, vulnerability.advisory, project_id)
    #    db.session.add(vul)
    #    db.session.commit()
        #vuls = Vulnerabilities.query.all()

        #vul  = Vulnerabilities(project_id,)
    #fp = file('results.xml', 'wb')
    #result = junitxml.JUnitXmlResult(fp)

    celery.send_task("joinertask", args=(project_id, 1))
    return 2


@celery.task(name="retiretask")
def retiretask(lang, repo, type, project_id):

    path = repo.split('/')[-1]
    name = path[:-4]
    path = '/tmp/repoTmpoR/' + name
    os.system('git clone '+repo+' '+path)
    #os.system('ls '+path)
    os.system('cd '+ path)
    os.chdir(path)
    os.system('npm install')
    os.system('retire --outputformat text --outputpath '+ path +'/checkba.txt')
    #fp = file('results.xml', 'wb')
    #result = junitxml.JUnitXmlResult(fp)
    #os.system('ls ' + path)

    f = open("checkba.txt", "r").readlines()
    cleared_results = []

    for x in f:
        if "has known vulnerabilities" in x:
            parsed = x.split(" ")
            default = ["no library", "no version", "no severity", "no summary", "no advisory"]
            library = parsed[0]
            version = parsed[1]
            if "severity" in x:
                severity = parsed[7]
            else:
                severity = ''
            summary  = x[x.find("summary"):].replace("\n", '')
            summary = x[x.find("advisory"):].replace("\n", '')
            vulnerability = Vulnerability(library, version, severity, summary, '')
            redis_db.hmset(project_id, {'%s' % id(vulnerability): vulnerability.__dict__})
            cleared_results.append(vulnerability)

    celery.send_task("joinertask", args=(project_id, 1))
    return 2


@app.route("/")
def hello():
    celery.send_task("mytask", args=(2, 3))
    return "hola"


@app.route("/check")
def check():
    lang = request.args['lang']
    repo = request.args['repo']
    type = request.args['type'] #zip or git

    project = Project(lang, repo, type, 1, 0)
    db.session.add(project)
    db.session.commit()
    #projects = Project.query.all()

    celery.send_task("checkertask", args=(lang, repo, type, project.id))
    #celery.send_task("retiretask", args=(lang, repo, type, project.id))
    return "checking"


if __name__ == "__main__":
    app.run()
    #filter(20)
    #filter(20)

