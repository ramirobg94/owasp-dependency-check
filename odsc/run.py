from security_dependency_check import (app, checker_app, miscellaneous_app,
                                       celery, home_app)

# --------------------------------------------------------------------------
# Build the app with the Blueprints
# --------------------------------------------------------------------------
app.register_blueprint(home_app)
app.register_blueprint(checker_app)
app.register_blueprint(miscellaneous_app)


if __name__ == '__main__':
    # app.run(host="127.0.0.1", port=8000)
    app.run(host="0.0.0.0", port=8001)
