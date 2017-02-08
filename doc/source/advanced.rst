Advanced deploy & config
========================

Manual launch
-------------

ODSC is written in Python, using Flask and Celery. The service is composed by two parts:

- Rest API (Flask)
- Analyzers (Celery processes)

We'll need to launch the two processes individually.

.. note::

    Pay attention to install the tools used by the analyzers before launch the service!

    see :ref:`binaries_required`

Launch Celery
+++++++++++++

.. code-block:: shell

    > cd odsc
    > celery -A run:celery worker -l INFO

Launch web application
++++++++++++++++++++++

.. code-block:: shell

    > cd odsc
    > gunicorn -w 4 run:app


.. _binaries_required:

Binaries required
-----------------

ODSC uses various software to launch the analysis. To do that, you need to install:

- retire: https://www.npmjs.com/package/retire
- OWASP Dependency Check: https://www.owasp.org/index.php/OWASP_Dependency_Check


Environment vars
----------------

You can customize the deployments setting some environments variables

- REDIS: Redis addr. Default: redis://localhost:6379
- CELERY_BACKEND. Celery backend used. Usually a database. Default: redis://localhost:6379
- CELERY_BROKER_URL: Broker used for distribute tasks. Default: redis://localhost:6379
- SQLALCHEMY_DATABASE_URI: Database DSN where store the results. Default: postgresql+pg8000://postgres:password@localhost/vulnerabilities
- ADDITIONAL_BINARY_PATHS: If your `retire` or `odsc` are not in the default system PATH, you can add more paths. Default: ":/usr/local/bin/"

Binaries required
-----------------

ODSC uses various software to launch the analysis. To do that, you need to install:

- **Retire**: https://www.npmjs.com/package/retire
- **OWASP Dependency Check**: https://www.owasp.org/index.php/OWASP_Dependency_Check