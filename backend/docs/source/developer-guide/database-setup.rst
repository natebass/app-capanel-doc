Setup the Database
================================================================

This section explains how to initialize the database and run the data import pipeline.

Cloud Run Database Initialization
---------------------------------

Once the schema exists, load the assessment data by running the research file importer. See :doc:`importing-research-files`.

### Using Fish Shell

To retrieve the Function URL and trigger the initialization:

.. code-block:: bash

    # 1. Get the Function URL
    set -lx FUNCTION_URL (gcloud functions describe capanel-full-init-trigger \
        --project ca-panel-001 \
        --region us-west1 \
        --gen2 \
        --format='value(serviceConfig.uri)')

    # 2. Get your identity token
    set -lx ID_TOKEN (gcloud auth print-identity-token)

    # 3. Trigger the full initialization
    curl -X POST "$FUNCTION_URL" \
            -H "Authorization: Bearer $ID_TOKEN" \
            -H "Content-Type: application/json" \
            -d '{"mode":"full","years":["2024","2025"],"wait_for_completion":true}'

### Triggering Both Imports

If you only need to trigger imports without a full rebuild:

.. code-block:: bash

    curl -X POST "$FUNCTION_URL" \
      -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
      -H "Content-Type: application/json" \
      -d '{"mode": "both_imports", "years": ["2024","2025"]}'

### Destructive Re-initialization

A full re-initialization that clears existing data requires explicit confirmation:

.. code-block:: bash

    curl -X POST "$FUNCTION_URL" \
      -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
      -H "Content-Type: application/json" \
      -d '{"mode": "full", "confirm_destructive": true}'

### Overwriting Data

To overwrite existing data for specific imports:

.. code-block:: bash

    curl -X POST "$FUNCTION_URL" \
      -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
      -H "Content-Type: application/json" \
      -d '{"mode": "both_imports", "overwrite": true, "confirm_overwrite": true}'

Local Database Initialization
-----------------------------

If you're running the import pipeline locally:

.. code-block:: bash

    python app/scripts/cde/run_import_pipeline.py --mode both_imports --resources-path <local_resources_path>

