from flask import Flask
from flask import request
from celery import Celery
#from urllib.parse import urlencode
#from urllib.parse import urlparse
#from gittle import Gittle
import os
from subprocess import call
import time
from vulnerability import Vulnerability
import xml.etree.ElementTree as ET

#repo_path = '/tmp/tmpRepo'
#repo_url = 'git://github.com/FriendCode/gittle.git'
#repo_path_b = repo_path.encode(encoding="ascii")
#repo_url_b = repo_url.encode(encoding="ascii")
#repo = Gittle.clone(repo_url_b, repo_path)

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

celery = make_celery(app)


@celery.task(name="mytask")
def add(x, y):
    print(x)
    return x + y

@celery.task(name="checkertask")
def checkertask(lang, repo, type):

    path = repo.split('/')[-1]
    name = path[:-4]
    path = '/tmp/repoTmpo/' + name
    os.system('git clone '+repo+' '+path)
    os.system('ls '+path)
    os.system('dependency-check --project "'+ repo +'"  --scan "'+ path +'" -f "XML" -o  "'+ path +'" --enableExperimental')

    tree = ET.parse(path + '/dependency-check-report.xml')
    root = tree.getroot()
    print(root)
    for vulnerability in root.findall('./dependencies'):
        print(vulnerability)
        #name = vulnerability.find('name').text
        #print(name)
    #fp = file('results.xml', 'wb')
    #result = junitxml.JUnitXmlResult(fp)
    os.system('ls ' + path)
    return 2


@celery.task(name="retiretask")
def retiretask(lang, repo, type):

    path = repo.split('/')[-1]
    name = path[:-4]
    path = '/tmp/repoTmpoR/' + name
    os.system('git clone '+repo+' '+path)
    #os.system('ls '+path)
    print(path)
    print(path + '/checkba.txt')
    print(path + '/package.json')
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
            advisory = x[x.find("advisory"):].replace("\n", '')
            vulnerability = Vulnerability(library, version, severity, summary, advisory)
            cleared_results.append(vulnerability)

    return 2


@app.route("/")
def hello():
    celery.send_task("mytask", args=(2, 3))
    return "hola"


@app.route("/check")
def check():
    lang = request.args['lang']
    repo = request.args['repo']
    type = request.args['type']
    celery.send_task("checkertask", args=(lang, repo, type))
    #celery.send_task("retiretask", args=(lang, repo, type))
    return "checking"


if __name__ == "__main__":
    app.run()

