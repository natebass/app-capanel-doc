
Format
```
#!/bin/sh -e
set -x

ruff check app scripts --fix
ruff format app scripts
```

Lint
```
#!/usr/bin/env bash

set -e
set -x

mypy app
ruff check app
ruff format app --check
```

Prestart
```
#! /usr/bin/env bash

set -e
set -x

# Let the DB start
python app/backend_pre_start.py

# Run migrations
alembic upgrade head

# Create initial data in DB
python app/initial_data.py
```

Tests
```
#!/usr/bin/env bash

set -e
set -x

coverage run -m pytest tests/
coverage report
coverage html --title "${@-coverage}"
```

Tests start
```
#! /usr/bin/env bash
set -e
set -x

python app/tests_pre_start.py

bash scripts/test.sh "$@"
```

Alembic Migration Environment
=============================

This document describes the configuration and execution flow of the Alembic migration environment used in the project.

Overview
--------

Generic single-database configuration.

The Alembic environment script (`env.py`) sets up the context for database migrations. It supports both **offline** and **online** migration modes and integrates with SQLModel metadata for autogeneration.

Configuration
-------------

- **Logging**: Logging is configured using the `.ini` file via `fileConfig`.
- **Metadata**: The metadata used for autogeneration is imported from `SQLModel.metadata`.

  .. code-block:: python

     from app.utility.models import SQLModel
     target_metadata = SQLModel.metadata

- **Environment Variables**: Database connection settings are sourced from `app.core.config.settings`.

Model Imports
-------------

To ensure all models are registered with SQLModel metadata, the following are imported:

.. code-block:: python

   from app.utility.models import User, Item, CensusData, School

Connection URL
--------------

The database URL is retrieved from the application settings:

.. code-block:: python

   def get_url():
       return str(settings.SQLALCHEMY_DATABASE_URI)

Migration Modes
---------------

Offline Mode
^^^^^^^^^^^^

In offline mode, Alembic generates SQL scripts without connecting to the database.

.. code-block:: python

   def run_migrations_offline():
       url = get_url()
       context.configure(
           url=url,
           target_metadata=target_metadata,
           literal_binds=True,
           compare_type=True
       )
       with context.begin_transaction():
           context.run_migrations()

Online Mode
^^^^^^^^^^^

In online mode, Alembic connects to the database and applies migrations directly.

.. code-block:: python

   def run_migrations_online():
       configuration = config.get_section(config.config_ini_section)
       configuration["sqlalchemy.url"] = get_url()
       connectable = engine_from_config(
           configuration,
           prefix="sqlalchemy.",
           poolclass=pool.NullPool,
       )
       with connectable.connect() as connection:
           context.configure(
               connection=connection,
               target_metadata=target_metadata,
               compare_type=True
           )
           with context.begin_transaction():
               context.run_migrations()

Execution Entry Point
---------------------

The script determines the mode and runs the appropriate migration function:

.. code-block:: python

   if context.is_offline_mode():
       run_migrations_offline()
   else:
       run_migrations_online()



# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.

.. code-block:: python

config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.

.. code-block:: python

fileConfig(config.config_file_name)
# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
# target_metadata = None

# Import all table models to ensure they are registered with SQLModel.metadata
from app.utility.models import User, Item, CensusData, School  # noqa

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

Where to look in the code
-------------------------
- app/main.py: creates the FastAPI app, CORS, and includes the API router.
- app/api/main.py: assembles the API router and registers all route modules.
- app/api/routes/: FastAPI route modules that expose endpoints.
- app/core/: configuration and infrastructure (settings, DB, security).
- app/models.py: data models.
- app/utils.py: helpers used across the codebase.
