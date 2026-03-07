Triggering Data Imports
================================================================

This guide explains how to manually trigger the data import pipeline on Google Cloud Platform using the Manual Init Trigger Cloud Function.

You can trigger the data import using either ``curl`` or the ``gcloud`` CLI.

Using curl
----------

To trigger the import using ``curl``, you need to provide an authorization token and the function URL.

.. code-block:: bash

    curl -X POST "https://us-west1-ca-panel-001.cloudfunctions.net/capanel-backend-init-trigger" \
        -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
        -H "Content-Type: application/json" \
        -d '{
            "mode": "both_imports",
            "gcs_uri": "gs://ca-panel-001-resources/resources",
            "resources_path": "/tmp/resources",
            "indicators_source": "cde",
            "indicators_path": "/tmp/resources/cde",
            "ela_files": [
                "/tmp/resources/cde/eladownload2024.xlsx",
                "/tmp/resources/cde/eladownload2025.xlsx"
            ],
            "years": ["2024", "2025"],
            "batch_size": 1000
        }'

Using gcloud
------------

Alternatively, you can use the ``gcloud functions call`` command, which is often more convenient if you have the ``gcloud`` SDK installed.

.. code-block:: bash

    gcloud functions call capanel-backend-init-trigger \
        --region=us-west1 \
        --data='{
            "mode": "both_imports",
            "gcs_uri": "gs://ca-panel-001-resources/resources",
            "resources_path": "/tmp/resources",
            "indicators_source": "cde",
            "indicators_path": "/tmp/resources/cde",
            "ela_files": [
                "/tmp/resources/cde/eladownload2024.xlsx",
                "/tmp/resources/cde/eladownload2025.xlsx"
            ],
            "years": ["2024", "2025"],
            "batch_size": 1000
        }'

Configuration Parameters
------------------------

The trigger function accepts the following JSON parameters:

*   ``mode``: The import mode (e.g., ``both_imports``, ``full``).
*   ``gcs_uri``: The Google Cloud Storage URI where the source data is located.
*   ``resources_path``: The local path in the container where resources will be synced.
*   ``indicators_source``: The source of the indicators (e.g., ``cde``).
*   ``indicators_path``: The path to the indicators data.
*   ``ela_files``: A list of ELA data files to process.
*   ``years``: A list of academic years to import.
*   ``batch_size``: The number of records to process in each batch.
