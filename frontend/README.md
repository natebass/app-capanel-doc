# California Accountability Panel frontend

This project is a copy of the main application frontend, but there are slight differences. The goals are:

- A simpler development environment without Docker.
- Experiment with components while previewing them with Storybook.
- Test the project extensively, in more ways than with the main application.

> [!Note]
> This project must be manually kept in sync by copy-pasting files to and from the main application. See the [sync documentation](https://opensacorg.github.io/app-capanel-doc/developer-guide/documentation-repository-sync).

## Overview

- [Developer Guide index](https://opensacorg.github.io/app-capanel-doc/developer-guide/)
- [Components guide](https://opensacorg.github.io/app-capanel-doc/developer-guide/components)
- [Storybook guide](https://opensacorg.github.io/app-capanel-doc/developer-guide/storybook)
- [Extended backend/frontend README reference](https://opensacorg.github.io/app-capanel-doc/developer-guide/readme-reference)

## Requirements

- [pnpm](https://pnpm.io/)

## Quick start

First, install the frontend dependencies.

- `cd frontend`
- `pnpm install`

> [!Warning]
> Before running anything, first create the required `.env` files. See [environment variable documentation](https://opensacorg.github.io/app-capanel-doc/developer-guide/environment-variables).

### Preview the documentation

`pnpm storybook`

### Run the main application

`pnpm run dev`

## Common tasks

1. Generate OpenAPI client:
   - `pnpm run openapi-ts` (from `frontend/` with `openapi.json` prepared)
2. Run Playwright tests:
   - `cd backend`
   - `uv run fastapi dev`
   - `cd ../frontend`
   - `pnpm test`
