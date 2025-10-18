Install
================================================================

This backend is a FastAPI server that provides overviews of California school
standards. Use this guide to set up the project locally and build the docs.

Prerequisites
-------------
- Python 3.10+
- uv or pip, and a working virtual environment tool

Install and run
---------------

1. Create and activate a virtual environment, then install dependencies:

   - Using uv (recommended):
     uv sync

   - Using pip:
     pip install -e .

2. Configure environment variables as needed (see app/core/config.py for available
   settings). The most important are:

   - PROJECT_NAME
   - API_V1_STR (default: /api/v1)
   - ENVIRONMENT (e.g., local, staging, production)
   - SENTRY_DSN (optional)

3. Start the server:

   uvicorn app.main:app --reload

The OpenAPI docs will be available at http://127.0.0.1:8000/docs

Build documentation
-------------------

From the backend/docs directory you can build HTML docs with:

- make html (Linux/macOS) or
- .\make.bat html (Windows)

The site will be generated in build/html.

Where to look in the code
-------------------------
- app/main.py: creates the FastAPI app, CORS, and includes the API router.
- app/api/main.py: assembles the API router and registers all route modules.
- app/api/routes/: FastAPI route modules that expose endpoints.
- app/core/: configuration and infrastructure (settings, DB, security).
- app/models.py: data models.
- app/utils.py: helpers used across the codebase.