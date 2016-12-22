from security_dependency_check import app, checker_app

# --------------------------------------------------------------------------
# Build the app with the Blueprints
# --------------------------------------------------------------------------
app.register_blueprint(checker_app)


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=8000)
