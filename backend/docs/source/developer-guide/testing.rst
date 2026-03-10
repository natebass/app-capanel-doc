Testing
=======

This section describes how to run tests for the application.

Prerequisites
-------------

- Docker and Docker Compose
- Python 3.10+

Running Tests
-------------

We use several Python scripts to manage testing, located in `tests/scripts/`.

### Run all tests with Docker

To build the environment and run all tests, use:

.. code-block:: bash

   python tests/scripts/test.py

This script will:
1. Build the Docker images.
2. Start the services.
3. Run the tests inside the `backend` container.
4. Clean up the environment after completion.

### Local testing with Docker Compose

If you want to keep the containers running or have a more persistent local environment:

.. code-block:: bash

   python tests/scripts/test_local.py

### Running Backend Tests directly

To run pytest with coverage reporting:

.. code-block:: bash

   python tests/scripts/test_backend.py

This generates:
- A terminal coverage report.
- An HTML coverage report (located in `htmlcov/` by default).

Test Pre-start
--------------

The `tests_start.py` script is used internally to ensure the application is ready before running tests. It executes `app/tests_pre_start.py` to wait for dependencies like the database.
