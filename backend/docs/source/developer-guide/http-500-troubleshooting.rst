HTTP 500 Internal Server Error - Troubleshooting
===================================================

This guide documents potential causes and recovery steps for the **HTTP 500 Internal Server Error** in the California Accountability Panel (CAP) application, particularly when deployed to **Google Cloud Run**.

Common Causes
-------------

### 1. Database Connection Failures
The most common cause for an HTTP 500 error is the application being unable to connect to the Cloud SQL database.

*   **Secret Manager Issues**: The application retrieves the `POSTGRES_PASSWORD` from Google Secret Manager. If the secret `capanel-postgres-password` is missing, contains the wrong password, or the Cloud Run service account lacks the ``Secret Manager Secret Accessor`` role, the connection will fail.
*   **Cloud SQL Instance Name**: Ensure `CLOUD_SQL_INSTANCE_CONNECTION_NAME` in your `.env` file (and environment variables) correctly matches your GCP instance (e.g., ``project-id:region:instance-id``).
*   **VPC Connector**: If the database is only accessible via a private IP, ensure the Cloud Run service is correctly configured with a VPC connector and the necessary firewall rules.

### 2. Startup Data Import Failures
The application performs an automated data import from Google Cloud Storage (GCS) during the `startup` event (see ``app/main.py``).

*   **Blocking Imports**: If ``RUN_DATA_IMPORTS_BLOCKING`` is set to ``True``, any failure during the import process (e.g., GCS bucket unreachable, network timeout, or invalid file format) will cause the application to fail to start or respond with a 500 error during initialization.
*   **GCS Permissions**: The Cloud Run service account must have ``Storage Object Viewer`` permissions on the bucket specified by ``IMPORT_GCS_URI``.
*   **PostgreSQL Advisory Locks**: The application uses advisory locks (``pg_try_advisory_lock``) to prevent concurrent imports. If a lock is held by a failed instance, it might cause issues (though it should time out or be released).

### 3. Database Schema Mismatches
If the database schema does not match the SQLModel definitions in the code, queries will fail.

*   **Alembic Migrations**: Ensure that migrations have been successfully applied. You can run the ``backend-init-job`` or trigger the ``manual-backend-init`` Cloud Function to run migrations and seed the database.
*   **Missing Tables/Columns**: If you see errors related to missing relations (e.g., ``relation "academicindicator" does not exist``), it means the initialization job has not been run or failed.

### 4. Sentry Integration
If `SENTRY_DSN` is configured, errors should be reported to Sentry.

*   Check your Sentry dashboard for the TraceID (e.g., ``0x760520b495788426``) to see the full stack trace and the exact exception that caused the 500 error.
*   If Sentry itself is misconfigured or unreachable, it should not cause a 500 error due to how the SDK is initialized, but it's worth verifying.

Diagnostic Steps
----------------

1.  **Check Cloud Run Logs**:
    Use the Google Cloud Console or `gcloud` to inspect the logs for your service:
    .. code-block:: bash

        gcloud logs read --service=capanel-backend --region=us-west1 --limit=50

2.  **Verify Secrets**:
    Ensure the secrets are correctly populated:
    .. code-block:: bash

        uv run backend/app/scripts/gcp/create_secrets.py .env

3.  **Run Manual Initialization**:
    Trigger the database initialization and import pipeline manually:
    .. code-block:: bash

        FUNCTION_URL=$(gcloud functions describe capanel-full-init-trigger --region us-west1 --gen2 --format="value(serviceConfig.uri)")
        curl -X POST -H "Authorization: Bearer $(gcloud auth print-identity-token)" "$FUNCTION_URL"

4.  **Health Check**:
    The application provides a basic health check endpoint at ``/api/v1/utils/health-check/``. If this returns ``true`` but other endpoints fail, the issue is likely database-related rather than a startup failure.

Recovery
--------

*   **Redeploy**: If the configuration was changed, redeploy the service to ensure all environment variables are correctly applied:
    .. code-block:: bash

        uv run backend/app/scripts/gcp/deploy_cloud_run.py .env --full-only
*   **Check Database Logs**: Inspect Cloud SQL logs for any authentication failures or aborted connections.
