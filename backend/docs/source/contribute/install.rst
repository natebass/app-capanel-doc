Install
================================================================

The backend uses FastAPI server and Postgres. Use this guide to set up the project locally and build the docs.

Prerequisites
-------------
- Python 3.10+
- uv or pip, and a working virtual environment tool
- PostgreSQL

Install and run
---------------

1. Create and activate a virtual environment, then install dependencies:

   - Using uv (recommended):
     uv sync --all-groups

   - Using pip:
     pip install -e .

2. Configure environment variables as needed (see app/core/config.py for available
   settings).

.. code-block:: bash
   :caption: .env

    # Domain
    # This would be set to the production domain with an env var on deployment
    # used by Traefik to transmit traffic and aqcuire TLS certificates
    DOMAIN=localhost
    # To test the local Traefik config
    # DOMAIN=localhost.tiangolo.com

    # Used by the backend to generate links in emails to the frontend
    FRONTEND_HOST=http://localhost:5173
    # In staging and production, set this env var to the frontend host, e.g.
    # FRONTEND_HOST=https://dashboard.example.com

    # Environment: local, staging, production
    ENVIRONMENT=local

    PROJECT_NAME="Full Stack FastAPI Project"
    STACK_NAME=full-stack-fastapi-project

    # Backend
    BACKEND_CORS_ORIGINS="http://localhost,http://localhost:5173,https://localhost,https://localhost:5173,http://localhost.tiangolo.com"
    SECRET_KEY=changethis
    FIRST_SUPERUSER=admin@example.com
    FIRST_SUPERUSER_PASSWORD=changethis

    # Emails
    SMTP_HOST=
    SMTP_USER=
    SMTP_PASSWORD=
    EMAILS_FROM_EMAIL=info@example.com
    SMTP_TLS=True
    SMTP_SSL=False
    SMTP_PORT=587

    # Postgres
    POSTGRES_SERVER=localhost
    POSTGRES_PORT=5432
    POSTGRES_DB=app
    POSTGRES_USER=postgres
    POSTGRES_PASSWORD=changethis

    SENTRY_DSN=

    # Configure these with your own Docker registry images
    DOCKER_IMAGE_BACKEND=backend
    DOCKER_IMAGE_FRONTEND=frontend


3. Start the server:

   uvicorn app.main:app --reload

The OpenAPI docs will be available at http://127.0.0.1:8000/docs

Build documentation
-------------------

From the backend/docs directory you can build HTML docs with:

- make html (Linux/macOS) or
- .\make.bat html (Windows)

The site will be generated in build/html.
