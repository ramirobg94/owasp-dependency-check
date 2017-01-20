Open Dependency Security Checker (ODSC)
=======================================

*aiotasks: A Celery like task manager for the new AsyncIO Python module*

.. image::  doc/logo-small.png
    :height: 64px
    :width: 64px
    :alt: ODSC logo

+----------------+--------------------------------------------------------------------+
|Project site    | https://github.com/ramirobg94/owasp-dependency-check               |
+----------------+--------------------------------------------------------------------+
|Issues          | https://github.com/ramirobg94/owasp-dependency-check/issues/       |
+----------------+--------------------------------------------------------------------+
|Documentation   | https://aiotasks.readthedocs.org/                                  |
+----------------+--------------------------------------------------------------------+
|Author          | Ramiro Blázquez / Daniel Garcia (cr0hn)                            |
+----------------+--------------------------------------------------------------------+
|Latest Version  | 1.0.0                                                              |
+----------------+--------------------------------------------------------------------+
|Python versions | 3.5 or above                                                       |
+----------------+--------------------------------------------------------------------+


Install From Docker
===================


.. code-block:: bash

    # docker run cr0hn/odsc

Install From source
===================

.. code-block:: bash

    # pip install -r odsc/requirements.txt

Binary requisites
-----------------

ODSC uses various software to launch the analysis. To do that, you need to install:

- retire: https://www.npmjs.com/package/retire
- OWASP Dependency Check: https://www.owasp.org/index.php/OWASP_Dependency_Check

Environment vars
----------------

- REDIS: Redis addr. Default: redis://localhost:6379
- CELERY_BACKEND. Celery backend used. Usually a database. Default: redis://localhost:6379
- CELERY_BROKER_URL: Broker used for distribute tasks. Default: redis://localhost:6379
- SQLALCHEMY_DATABASE_URI: Database DSN where store the results. Default: postgresql+pg8000://postgres:password@localhost/vulnerabilities
- ADDITIONAL_BINARY_PATHS: If your `retire` or `owasp-dependency-check` are not in the default system PATH, you can add more paths. Default: ":/usr/local/bin/"

Launch Celery
-------------

.. code-block:: bash

    # cd odsc
    # celery -A run:celery worker -l INFO

Launch web application
----------------------

.. code-block:: bash

    # cd odsc
    # gunicorn -w 4 run:app

Using the project
=================

Using a browser
---------------

Launch a browser and type the addr: `http://127.0.0.1:8000`.

Using console
-------------

.. code-block:: bash

    # curl "http://127.0.0.1:8000/api/v1/check?lang=nodejs&repo=https://github.com/ramirobg94/QuizCore"

License
=======

This project is distributed under MIT license