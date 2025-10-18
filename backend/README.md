Install
================================================================

AI generated.

Goal
----
Document the FastAPI backend that exposes overviews of school standards so new
contributors and API consumers can understand, run, and extend the service. Use
Sphinx autodoc and type hints to keep the API reference up‑to‑date with code.

What to document
----------------
1. Overview and purpose
	- What the service does: provide programmatic access to school standards
        overviews and related resources.
	- Primary personas: API consumers (frontends, integrations) and contributors.

2. Architecture
	- High‑level diagram/description of the main pieces:
	  - app/main.py: FastAPI app construction, CORS, Sentry.
	  - app/api/main.py: API router assembly.
	  - app/api/routes/*: individual route modules grouped by domain.
	  - app/core/*: configuration, database, security concerns.
	  - app/models.py: data models used by routes/CRUD.
	  - app/crud.py: data access helpers.
	  - app/utils.py: shared utilities.

3. Running locally (Get Started)
	- Prerequisites, environment variables, how to run uvicorn, where to find the
	  OpenAPI UI, and how to run tests.

4. Configuration
	- app.core.config.Settings: environment variables, defaults, and behavior.
	- How to override per‑environment (ENVIRONMENT, API_V1_STR, SENTRY_DSN, etc.).

5. API surface (generated with autodoc)
	- app.main and app.api.main: application and router wiring.
	- app.api.routes.*: public endpoints grouped by module; include docstrings for
	  each path operation explaining inputs, outputs, and notes.

6. Data models
	- app.models: important classes/structures; clarify persistence vs payload
	  models if applicable; include type hints for clarity in docs.

7. Persistence and data access
	- app.core.db and app.crud: how the DB connection/session is managed and how
	  CRUD helpers are intended to be used from routes.

8. Security
	- app.core.security: authentication/authorization utilities used by routes,
	  expected headers/tokens, and common pitfalls.

9. Utilities
	- app.utils: common helper functions and their typical usage.

10. Conventions and contributing
	 - Coding standards, typing, testing patterns, how to add a new route module
		and have it appear in the docs automatically (ensure docstrings and types).

How it is organized in this site
--------------------------------
- Get started: quickstart to set up and run the server and build docs.
- API Reference: auto‑generated module reference leveraging type hints
  (sphinx.ext.autodoc + sphinx_autodoc_typehints).

Actions to keep docs healthy
----------------------------
- Prefer comprehensive type hints; autodoc will include them in signatures.
- Write docstrings for modules, classes, and functions, especially route
  handlers (explain parameters and response models).
- When adding a module, ensure it is importable and included under app/ so the
  modules.rst page can autodoc it.
