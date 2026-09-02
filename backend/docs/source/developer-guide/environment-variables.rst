Add environment variables
================================================================
Configure environment variables as needed (see ``app/core/config.py`` for available settings).

.. code-block:: bash
   :caption: .env

    # General
    PROJECT_NAME="California Accountability Panel"
    # Only "development" is accepted; leave it unset everywhere else.  Unset is
    # the strict mode: a "changethis" secret raises instead of warning, and the
    # development-only API routes are not registered.
    FASTAPI_ENV=development

    # Frontend
    FRONTEND_HOST=http://localhost:5173
    FRONTEND_HOST_PRODUCTION=https://capanel.example.org

    # Backend
    BACKEND_CORS_ORIGINS="http://localhost,http://localhost:5173,https://localhost,https://localhost:5173,https://capanel.example.org"
    SECRET_KEY=<Set from SSM Parameter Store as `/capanel/secret-key` when deployed>
    FIRST_SUPERUSER=<Set an initial superuser>
    FIRST_SUPERUSER_PASSWORD=<Set an initial superuser password>

    # Local Postgres
    DB_CONNECTION_MODE=local
    POSTGRES_SERVER=localhost
    POSTGRES_PORT=5432
    POSTGRES_DB=<Your local Postgres database name>
    POSTGRES_USER=<Your local Postgres username>
    POSTGRES_PASSWORD=<Your local Postgres password>

    # Deployment (Docker on EC2, see the AWS deployment guide)
    AWS_REGION="us-west-2"
    SITE_ADDRESS="capanel.example.org"

    # Data Import
    RESEARCH_FILE_SOURCE_URI="s3://capanel-007361225089-us-west-2-an/resources/california-state"
    # Dashboard files default to the state's own web server; point this at the
    # uploaded copies to pin the import to files you have already checked.
    # DASHBOARD_FILE_SOURCE_URI="s3://capanel-007361225089-us-west-2-an/resources/cde-2025"

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

.. note::

   This applies when the front end is hosted separately, such as on GitHub
   Pages. In the Docker deployment described in :doc:`aws-deployment`, Caddy
   serves the built front end and proxies ``/api`` to the backend on the same
   origin, so ``VITE_API_URL`` is left empty and CORS never comes into it.

When the two are hosted separately they are on different origins, so the browser
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

Secrets
================================================================

In deployed environments ``SECRET_KEY``, ``POSTGRES_PASSWORD`` and
``FIRST_SUPERUSER_PASSWORD`` are not kept in a checked-in file. They live in
**AWS Systems Manager Parameter Store** as ``SecureString`` parameters under
``/capanel/``, and the deploy script on the instance materialises them into the
``.env`` that Docker Compose reads.

Parameter Store rather than Secrets Manager: standard parameters, including
encrypted ones, are free, while Secrets Manager bills $0.40 per secret per
month for the same thing at this scale.

.. code-block:: bash

    aws ssm put-parameter --name /capanel/secret-key \
      --type SecureString --value "$(openssl rand -hex 32)"

    aws ssm put-parameter --name /capanel/postgres-password \
      --type SecureString --value "$(openssl rand -hex 24)"

The instance reads them through its instance profile, so no access keys exist on
disk. Rotating a value is ``put-parameter --overwrite`` followed by re-running
``deploy.sh``, which rewrites ``.env`` and restarts the containers. See
:doc:`aws-deployment` for the IAM policy and :doc:`security` for the rotation
procedure.
