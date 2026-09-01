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

Front-end build variables
================================================================

The front end is a static build deployed on its own, separately from the API. Two
variables tell it where it will live and where the API is. Both are read at build
time and baked into the bundle, so a change to either needs a rebuild.

.. code-block:: bash
   :caption: frontend/.env

    # Path the built site is served from. Leave unset (or "/") for a naked
    # custom domain; set the repository path for a GitHub Pages project site.
    VITE_BASE_PATH=/
    # Public origin of the API. Leave unset during local development: the Vite
    # dev server proxies /api, /docs, and /redoc to http://localhost:8000.
    VITE_API_URL=https://api.example.org

``VITE_BASE_PATH``
    ``/`` (or unset) builds for the root of a domain, such as
    ``https://example.org/``. A repository path such as ``app-capanel-web``
    builds for ``https://opensacorg.github.io/app-capanel-web/``; leading and
    trailing slashes are added when missing. The value also becomes the router's
    base path, so links and deep links stay correct under a sub-path.

    A value starting with ``.`` (such as ``./``) produces fully relative asset
    URLs. That suits a site whose final path is unknown at build time, but a hard
    reload of a nested route then resolves its assets against the wrong
    directory, so prefer the explicit path whenever it is known.

``VITE_API_URL``
    The origin the generated client calls, for example
    ``https://api.example.org``. A trailing ``/api`` or ``/api/v1`` is trimmed,
    so either form works. Because the front end and the API are on different
    origins in production, the front end's own origin has to be allowed by the
    backend, as described next.

Cross-origin requests
================================================================

The front end and the API are served from different origins, so the browser
applies CORS to every API call and the backend has to name each origin it will
accept. ``app/main.py`` passes :attr:`Settings.all_cors_origins` to FastAPI's
``CORSMiddleware``, which combines:

``FRONTEND_HOST``
    The public base URL of the front end. It is also used to build links in
    emails, so it keeps any sub-path: a GitHub Pages project site is
    ``https://opensacorg.github.io/app-capanel-web``.

``BACKEND_CORS_ORIGINS``
    A comma-separated list of any further origins, for when the same deployment
    is reachable under more than one name, such as a Pages sub-domain and a
    custom domain.

Each entry is reduced to the ``scheme://host:port`` origin a browser actually
sends in the ``Origin`` header, so a path or a trailing slash on either variable
is harmless.

.. warning::

   A request that is blocked by CORS still succeeds under ``curl``, because only
   browsers enforce it. A deployed site whose API calls fail while the same URL
   works from a terminal almost always means the site's origin is missing here.

Every build writes two extra files next to ``index.html`` for static hosts:
``404.html`` (a copy of ``index.html``, which GitHub Pages serves for unknown
paths so deep links reach the client-side router) and ``.nojekyll`` (which stops
Pages from running the output through Jekyll). Both are ignored by other hosts.

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
