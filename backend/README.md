# California Accountability Panel back-end documentation

This project is a copy of the main application back-end, but there are slight differences. The goals are:

- Use Sphinx to generate documentation with autodoc.
- Test the project extensively, in more ways than with the main application.
- A simpler development environment without Docker.

> **Note:** This project must be manually kept in sync by copy-pasting files to and from the main application. See the [sync documentation](https://opensacorg.github.io/app-capanel-doc/developer-guide/documentation-repository-sync).

## Prerequisites

- [uv](https://docs.astral.sh/uv/)

## Quick start

First, install the back-end dependencies.
- `cd backend`
- `uv sync`

> [!Warning]
> Before running anything, first create the required `.env` files. See [environment variable documentation](https://opensacorg.github.io/app-capanel-doc/developer-guide/environment-variables).

> [!Note]
> Python commands must be run from the backend folder. It is recommended to open the backend folders separately in VS Code. To run from the root of the project, it is recommended to use Make.  

### Run the sphinx autoload

```
sphinx-autobuild docs/source docs/build/html
```

You can also run with Make. Be aware that this will create a .venv folder inside of backend/docs. This might be confusing.

## Run the application

### Initialize the database

Initialize the database. This will run the migrations and create a default superuser.

```
uv run app/scripts/initial_data.py
```

### Start the local development server

- From the backend folder: `uv run --env-file ../.env fastapi dev`
- From the root of the project: `uv run fastapi dev backend/app/main.py`.


## Resources

- [Developer Guide](https://opensacorg.github.io/app-capanel-doc/developer-guide/)
- [Install](https://opensacorg.github.io/app-capanel-doc/developer-guide/install/)
- [Development workflow](https://opensacorg.github.io/app-capanel-doc/developer-guide/development)
- [Run application](https://opensacorg.github.io/app-capanel-doc/developer-guide/run-application)
- [Testing](https://opensacorg.github.io/app-capanel-doc/developer-guide/testing)
- [Extended backend/frontend README reference](https://opensacorg.github.io/app-capanel-doc/developer-guide/readme-reference)
