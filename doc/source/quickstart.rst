Quick Start
===========


.. _quick_start:

Install using Docker Compose
----------------------------

ODSC use various services (like Redis or PostgresSQL) that you need to install and configure. So the most easly wat to desploy ODSC is using `docker-compose`:

1. **Download the project code**

.. code-block:: shell

    > git clone https://github.com/BBVA/ODSC.git /tmp/odsc

2. **Go to the source code installation**

.. code-block:: shell

    > cd /tmp/odsc

3. **Run `Docker compose` to deploy the service:**

.. code-block:: shell

    > docker-compose build & docker-compose up

4. **Use the project**

4.1. *Using web browser*

    Open your web browser to the address: http://127.0.0.1:

    .. image::  _static/screenshot-001.jpg
        :width: 90%
        :align: center
    |

    .. image::  _static/screenshot-002.jpg
        :width: 90%
        :align: center

4.2. *Using in console with CURL*

    Very easy, after deploy the service, you only need to run a simple `curl` in a console:

    .. code-block:: shell

        > curl http://127.0.0.1/api/v1/project/create?lang=nodejs&repo=https://github.com/ramirobg94/QuizCore
        {project: ñaskdjflasjfklas}

    Now check the status:

    .. code-block:: shell

        > curl http://127.0.0.1/api/v1/project/status/
        {scan_status: "running"}

    And, when finished, get results:

    .. code-block:: shell

        > curl http://127.0.0.1/api/v1/project/results/