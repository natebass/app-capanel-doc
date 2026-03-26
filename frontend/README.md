# California Accountability Panel front-end documentation

This project is a copy of the main application front-end, but there are slight differences. The goals are:

- Test the project extensively, in more ways than with the main application.
- Experiment with components while previewing them with Storybook.
- A simpler development environment without Docker.

> [!Note]
> This project must be manually kept in sync by copy-pasting files to and from the main application. See the [sync documentation](https://opensacorg.github.io/app-capanel-doc/developer-guide/documentation-repository-sync).

## Prerequisites

- [pnpm](https://pnpm.io/)

## Quick start

First, install the front-end dependencies.

- `cd frontend`
- `pnpm install`

> [!Warning]
> Before running anything, first create the required `.env` files. See [environment variable documentation](https://opensacorg.github.io/app-capanel-doc/developer-guide/environment-variables).

> [!Note]
> PNPM commands must be run from the frontend folder. It is recommended to open the frontend folder directly in VSCode. To run from the root of the project, it is recommended to use Make.

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

## Resources

- [Developer Guide index](https://opensacorg.github.io/app-capanel-doc/developer-guide/)
- [Components guide](https://opensacorg.github.io/app-capanel-doc/developer-guide/components)
- [Storybook guide](https://opensacorg.github.io/app-capanel-doc/developer-guide/storybook)
- [Extended backend/frontend README reference](https://opensacorg.github.io/app-capanel-doc/developer-guide/readme-reference)
