# California Accountability Panel backend

This project is a copy of the main application backend, but there are slight differences. The goals are:

- A simpler development environment without Docker.
- Use Sphinx to generate documentation with autodoc.
- Test the project extensively, in more ways than with the main application.

> **Note:** This project must be manually kept in sync by copy-pasting files to and from the main application. See the [sync documentation](https://opensacorg.github.io/app-capanel-doc/developer-guide/documentation-repository-sync).

## Overvie  w

- [Developer Guide](https://opensacorg.github.io/app-capanel-doc/developer-guide/)
- [Install](https://opensacorg.github.io/app-capanel-doc/developer-guide/install/)
- [Development workflow](https://opensacorg.github.io/app-capanel-doc/developer-guide/development)
- [Run application](https://opensacorg.github.io/app-capanel-doc/developer-guide/run-application)
- [Testing](https://opensacorg.github.io/app-capanel-doc/developer-guide/testing)
- [Extended backend/frontend README reference](https://opensacorg.github.io/app-capanel-doc/developer-guide/readme-reference)

## Requirements

- [uv](https://docs.astral.sh/uv/)

## Quickstart

First, install the backend dependencies.
- `cd backend`
- `uv sync`

> [!Warning]
> Before running anything, first create the required `.env` files. See [environment variable documentation](https://opensacorg.github.io/app-capanel-doc/developer-guide/environment-variables).

### Initialize the database

If you haven't already done so, initialize the database. This will run the migrations and create a default super user.

`uv run app/scripts/initial_data.py`

### Start the local development server
`uv run --env-file ../.env fastapi dev`
or from the root of the project:
`uv run --env-file .env fastapi dev backend\app\main.py`
