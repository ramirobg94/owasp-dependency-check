from flask import Flask
from flask import request
from celery import Celery
from git import Repo



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
    print(lang)
    print(repo)
    print(type)
    g = git.cmd.Git('git@github.com:ramirobg94/pruebaR.git')
    d.pull()
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
