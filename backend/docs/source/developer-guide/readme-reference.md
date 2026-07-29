# README Extended Reference

This page contains detailed operational notes that were removed from repository README files to keep those files concise.

## Documentation workflows

1. Sync backend dependencies before running documentation tools:
   - `cd backend`
   - `uv sync`
2. Build or preview Sphinx docs from `backend/docs`:
   - `make html`
   - `make preview`
   - `make reload` (live reload)
3. Alternative direct Sphinx build command:
   - `uv run sphinx-build -b html source build/html`
4. Optional live server with auto rebuild:
   - `uv run sphinx-autobuild source build/html --open-browser`

## Documentation troubleshooting

- `sphinxcontrib.mermaid` import error:
  - `cd backend`
  - `uv add sphinxcontrib-mermaid`
- `make reload` target not found:
  - run commands from `backend/docs`
- `sphinx-build` command not found:
  - use `uv run sphinx-build ...`
- Port `8000` already in use:
  - run preview on another port (for example `python -m http.server 8001` from `build/html`)

## Frontend client generation

1. Automatic generation from project root:
   - `python backend/app/scripts/generate_client.py`
2. Manual generation:
   - Download `http://localhost/api/v1/openapi.json` to `frontend/openapi.json`
   - `cd frontend`
   - `pnpm run openapi-ts`
3. Regenerate whenever backend OpenAPI schema changes.

## Frontend remote API configuration

1. Set `VITE_API_URL` in `frontend/.env`.
2. Example:

   ```text
   VITE_API_URL=https://api.my-domain.example.com
   ```

## Frontend Playwright tests

1. Start required backend service:
   - `docker compose up -d --wait backend`
2. Run tests:
   - `cd frontend`
   - `pnpm exec playwright test`
3. Optional UI mode:
   - `pnpm exec playwright test --ui`
4. Cleanup stack and test data:
   - `docker compose down -v`

## Backend operations

1. Start local stack:
   - `docker compose watch`
2. Open a shell in the backend container when needed:
   - `docker compose exec backend bash`
3. Run backend tests in a running stack:
   - `docker compose exec backend bash scripts/tests-start.sh`

## Database migrations

1. Open backend container shell:
   - `docker compose exec backend bash`
2. Create migration revision after model changes:
   - `alembic revision --autogenerate -m "Describe schema change"`
3. Apply migration:
   - `alembic upgrade head`

## Related Developer Guide pages

- [Install](install/index)
- [Development](development)
- [Run application](run-application)
- [Testing](testing)
- [Sphinx](sphinx)
- [Storybook](storybook)
- [Components](components)