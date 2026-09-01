HTTP 500 Internal Server Error - Troubleshooting
===================================================

This guide documents potential causes and recovery steps for the **HTTP 500 Internal Server Error** in the California
Accountability Panel (CAP) application, in the Docker deployment described in :doc:`aws-deployment`.

Common Causes
-------------

1. Database connection failures
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The most common cause of an HTTP 500 is the backend being unable to reach PostgreSQL.

*   **Missing or wrong password**: ``DATABASE_URL`` is built in ``compose.yaml`` from ``POSTGRES_USER`` and
    ``POSTGRES_PASSWORD`` in ``.env``, which ``deploy.sh`` writes from SSM Parameter Store. If the parameter was
    rotated but ``deploy.sh`` has not been re-run, the backend still holds the old value.
*   **The database container is not healthy**: ``docker compose ps`` shows its health. The ``backend`` service waits on
    ``service_healthy``, so a backend that started at all means the database was up at the time — it may have gone away
    since.
*   **The volume filled up**: PostgreSQL refuses writes when the disk is full, which surfaces as 500s on anything that
    writes. Check with ``df -h``; an import that was interrupted mid-way is the usual reason.

2. Import failures
~~~~~~~~~~~~~~~~~~

*   **S3 permissions**: The instance role must allow ``s3:GetObject`` on the ``resources/`` prefix and ``s3:ListBucket``
    on the bucket. A missing permission surfaces as an ``AccessDenied`` from ``boto3`` in the import output, not as a
    500 — but it leaves the database empty, and endpoints querying empty reference tables can fail.
*   **PostgreSQL advisory locks**: The importer uses ``pg_try_advisory_lock`` to prevent concurrent imports. A lock held
    by a container that was killed is released when its session ends; if an import refuses to start, confirm no other
    ``docker compose run`` is still going.

3. Database schema mismatches
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If the schema does not match the SQLModel definitions in the code, queries fail. Errors naming a missing relation, such
as ``relation "academicindicator" does not exist``, mean migrations have not been applied:

.. code-block:: bash

    docker compose run --rm backend alembic upgrade head

4. Sentry integration
~~~~~~~~~~~~~~~~~~~~~

If ``SENTRY_DSN`` is configured, errors are reported to Sentry. Check the dashboard for the TraceID to see the full
stack trace and the exact exception. A misconfigured or unreachable Sentry does not itself cause a 500.

Diagnostic Steps
----------------

1.  **Read the logs**:

    .. code-block:: bash

        docker compose logs -n 200 backend
        docker compose logs -n 50 db

2.  **Check the health endpoint**. The application exposes ``/api/v1/utils/health-check/``. If it returns ``true`` but
    other endpoints fail, the problem is a query or the data, not startup.

3.  **Open a shell against the database**:

    .. code-block:: bash

        docker compose exec db psql -U capanel -c "\dt"

4.  **Re-run the deploy**, which rewrites ``.env`` from Parameter Store, applies migrations and restarts:

    .. code-block:: bash

        ./deploy.sh

Recovery
--------

*   **Restart the stack**: ``docker compose up -d --force-recreate backend``.
*   **Reload the data**: the database is reproducible from S3 and the state's web server. See
    :doc:`importing-research-files`.
*   **Restore**: a daily EBS snapshot and a weekly ``pg_dump`` in S3 are described in :doc:`aws-deployment`.
