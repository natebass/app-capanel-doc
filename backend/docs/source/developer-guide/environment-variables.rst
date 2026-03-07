Add environment variables
================================================================
Configure environment variables as needed (see ``app/core/config.py`` for available settings).

.. code-block:: bash
   :caption: .env

    # General
    DOMAIN=localhost
    PROJECT_NAME="California Accountability Panel"
    # Environment: local, staging, production
    ENVIRONMENT=local

    # Frontend
    FRONTEND_HOST=http://localhost:5173
    FRONTEND_HOST_PRODUCTION=https://capanel-full-5418848943.us-west1.run.app

    # Backend
    BACKEND_CORS_ORIGINS="http://localhost,http://localhost:5173,https://localhost,https://localhost:5173,https://capanel-full-5418848943.us-west1.run.app"
    SECRET_KEY=<Set by Google Secret Manager as `capanel-secret-key`>
    FIRST_SUPERUSER=<Set an initial superuser>
    FIRST_SUPERUSER_PASSWORD=<Set an initial superuser password>

    # Local Postgres
    DB_CONNECTION_MODE=local
    POSTGRES_SERVER=localhost
    POSTGRES_PORT=5432
    POSTGRES_DB=<Your local Postgres database name>
    POSTGRES_USER=<Your local Postgres username>
    POSTGRES_PASSWORD=<Your local Postgres password>

    # Google Cloud Platform (GCP)
    GCP_PROJECT_ID="ca-panel-001"
    GCP_REGION="us-west1"
    GCP_AR_REPOSITORY="capanel-repo"
    FULL_SERVICE="capanel-full"
    BACKEND_SERVICE="capanel-backend"
    FRONTEND_SERVICE="capanel-frontend"
    RUN_SERVICE_ACCOUNT="capanel-runner"
    VPC_NETWORK="default"
    VPC_SUBNET="default"

    # Cloud SQL
    CLOUD_SQL_INSTANCE="capanel-pg"
    CLOUD_SQL_DB="capanel"
    CLOUD_SQL_USER="capanel_app"
    CLOUD_SQL_PASSWORD=<Set by Google Secret Manager as `capanel-postgres-password`>
    CLOUD_SQL_VERSION="POSTGRES_18"
    CLOUD_SQL_EDITION="enterprise"
    CLOUD_SQL_INSTANCE_CONNECTION_NAME="ca-panel-001:us-west1:capanel-pg"

    # Data Import
    IMPORT_RESOURCES_HOST_PATH=<Your resource folder, like ~/Downloads/resources.>
    IMPORT_GCS_URI="gs://capanel-resources"

Google Secret Manager
================================================================

In production environments, sensitive information such as ``SECRET_KEY`` and ``CLOUD_SQL_PASSWORD`` should not be stored in plain text environment variables. Instead, the project uses **Google Secret Manager** to securely store and manage these secrets.

How it works
------------

1.  **Storage**: Secrets are stored in GCP Secret Manager under specific names:
    *   ``capanel-secret-key``: Maps to the ``SECRET_KEY`` environment variable.
    *   ``capanel-postgres-password``: Maps to the ``POSTGRES_PASSWORD`` environment variable for database authentication.
2.  **Access Control**: The Cloud Run service account (defined by ``RUN_SERVICE_ACCOUNT``) is granted the ``roles/secretmanager.secretAccessor`` role for these specific secrets.
3.  **Deployment**: During deployment, the Cloud Run service is configured to map these secrets to environment variables.

Managing Secrets
----------------

The project includes a utility script to create and update secrets in Secret Manager:

.. code-block:: bash

    python app/scripts/gcp/create_secrets.py

This script:
*   Enables the Secret Manager API.
*   Creates the secrets if they don't exist.
*   Adds a new version with the value from your local ``.env`` file.
*   Grants access to the Cloud Run service account.
