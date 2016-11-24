from flask import Flask
from celery import Celery
from celery import task

app = Flask('checker')

celery = Celery('tasks', broker='amqp://localhost')

@task
def add(x, y):
    print(x)
    return x+y

@app.route("/")
def hello():
    task = add.delay(2,3)
    return task

if __name__ == "__main__":
    app.run()