Setup the Database
================================================================

This section explains how to initialize the database and run the data import pipeline.

The schema comes from Alembic; the data comes from the importers. Both layers —
assessment and accountability — are loaded separately, and the importers are safe to
re-run: a file whose size and entity tag are unchanged since the last successful load
is skipped.

Deployed initialization
-----------------------

On the EC2 instance described in :doc:`aws-deployment`, everything runs as a one-off
container against the running stack. ``deploy.sh`` already applies migrations and
seeds the first superuser; the data import is a separate, deliberate step because it
takes about an hour.

.. code-block:: bash

    cd /opt/capanel

    # Schema and the initial superuser (also done by deploy.sh).
    docker compose run --rm backend alembic upgrade head
    docker compose run --rm backend python app/scripts/initial_data.py

    # Assessment layer: CAASPP and ELPAC statewide research files, from S3.
    docker compose run --rm backend python app/scripts/ingest_research_files.py \
      --source s3://capanel-007361225089-us-west-2-an/resources/california-state

    # Accountability layer: California School Dashboard indicators.
    docker compose run --rm backend python app/scripts/ingest_dashboard_files.py --year 2024
    docker compose run --rm backend python app/scripts/ingest_dashboard_files.py --year 2025

    # LCFF local indicators, growth model, census-day enrollment.
    docker compose run --rm backend python app/scripts/ingest_local_indicators.py --year 2025
    docker compose run --rm backend python app/scripts/ingest_growth.py
    docker compose run --rm backend python app/scripts/ingest_enrollment.py

The dashboard, growth and enrollment importers read from ``www3.cde.ca.gov`` by
default, so no local copy is needed. Pass ``--source`` with an ``s3://`` prefix to use
the uploaded workbooks instead.

Reloading a year
~~~~~~~~~~~~~~~~

To force a reload of files whose fingerprint has not changed, add ``--force``:

.. code-block:: bash

    docker compose run --rm backend python app/scripts/ingest_research_files.py \
      --year 2025 --only sb_ --force

Local initialization
--------------------

The same scripts, without the container wrapper, from the ``backend`` directory:

.. code-block:: bash

    uv run alembic upgrade head
    uv run app/scripts/initial_data.py
    uv run app/scripts/ingest_research_files.py --source ~/Downloads/resources/california-state
    uv run app/scripts/ingest_dashboard_files.py --year 2025

``RESEARCH_FILE_SOURCE_URI`` in ``.env`` sets the default source, so ``--source`` is
only needed to override it. A local directory is searched recursively, so one folder
holding several years of downloads loads in a single pass.

Expect the full assessment import to leave the database around 10 GB.

See :doc:`importing-research-files` for the importer's full option list, and
:doc:`database-troubleshooting` when a load does not go as planned.
