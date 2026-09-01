# California Accountability Panel back-end documentation

- Use Sphinx to generate documentation with autodoc.
- Test the project extensively, in more ways than with the main application.
- A simpler development environment without Docker.

## Prerequisite

- [uv](https://docs.astral.sh/uv/)
- [PostgreSQL]([https://docs.astral.sh/uv/](https://www.postgresql.org/))

## Development

For development, it is recommended to open the backend folder directly in VSCode and run Python commands as normal.

First, install the backend dependencies.
- `cd backend`
- `uv sync`

### Documentation

If you are only concerned with documentation, you do not need to run the application.

```shell
sphinx-autobuild docs/source docs/build/html
```

Equivalent to `make reload`.

### FastAPI

> [!Warning]
> Before running the application, first create an `.env` file in the root of the repository
> _and/or_ in the current (backend) directory.
> See
the [environment variable guide](https://opensacorg.github.io/app-capanel-doc/developer-guide/environment-variables).

#### 1. Initialize the database

Run the migrations and create a default superuser.

> [!Note]
> This does not populate the database with any dashboard data.
> See the [data guide](https://opensacorg.github.io/app-capanel-doc/developer-guide/run-application).

```shell
uv run app/scripts/initial_data.py
```

#### 2. Start the API

- `uv run fastapi dev` if the `.env` file is in the current (backend) directory.
- `uv run --env-file ../.env fastapi dev` if the `.env` file is in the root of the repository.

> If you see an error like `FIRST_SUPERUSER_PASSWORD Field required [type=missing, input_value={'FASTAPI_ENV': 'development'}, input_type=dict]
> For further information visit https://errors.pydantic.dev/2.13/v/missing`
> then you are likely missing an `.env` file.

## Resources

- [Developer Guide](https://opensacorg.github.io/app-capanel-doc/developer-guide/)
- [Install](https://opensacorg.github.io/app-capanel-doc/developer-guide/install/)
- [Development workflow](https://opensacorg.github.io/app-capanel-doc/developer-guide/development)
- [Run application](https://opensacorg.github.io/app-capanel-doc/developer-guide/run-application)
- [Testing](https://opensacorg.github.io/app-capanel-doc/developer-guide/testing)
- [Extended backend/frontend README reference](https://opensacorg.github.io/app-capanel-doc/developer-guide/readme-reference)
