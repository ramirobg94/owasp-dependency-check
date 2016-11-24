from flask import Flask
from celery import Celery


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


@app.route("/")
def hello():
    celery.send_task("mytask", args=(2, 3))
    
    return "hola"

if __name__ == "__main__":
    app.run()
