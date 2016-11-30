from flask import Flask
from flask import request
from celery import Celery
#from urllib.parse import urlencode
#from urllib.parse import urlparse
#from gittle import Gittle
import os
from subprocess import call
import time
import junitxml

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
    os.system('dependency-check --project "'+ repo +'"  --scan "'+ path +'" -f "HTML" -o  "'+ path +'" --enableExperimental')
    #fp = file('results.xml', 'wb')
    #result = junitxml.JUnitXmlResult(fp)
    os.system('ls ' + path)
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
    return "checking"


if __name__ == "__main__":
    app.run()
