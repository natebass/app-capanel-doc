Test repository sync
====================

The test repository is manually kept in sync with the main application.
When major changes are made in the main repository, copy and paste the
matching files into this docs/test repository.

The sync process is usually done in two parts: frontend and backend.

Frontend
--------

Copy these folders from the main repository into this repository:

- ``frontend/src/``
- ``frontend/public/``

Also copy frontend config files, with these exceptions:

- ``frontend/README.md``
- ``frontend/package.json``
- ``frontend/pnpm-lock.yaml``
- ``frontend/pnpm-workspace.yaml``

Use a normal copy operation and choose to replace all conflicting files.

The docs repository includes ``frontend/src/components/stories`` for Storybook,
while the main repository does not. This folder should remain in place after
syncing.

Notes:

- ``package.json`` is intentionally different here because of additional testing
  dependencies.
- Unlike the main website repository, docs do not use a root pnpm workspace.
  The frontend ``package.json`` lives inside the ``frontend`` folder.

Backend
-------

Copy this folder from the main repository into this repository:

- ``backend/app``

Do not copy ``README.md``.

Dependencies are slightly different in the docs repository. Update
``backend/pyproject.toml`` only when new dependencies are needed. In practice,
it is often easier to add missing dependencies with ``uv add`` instead of
manually diffing the file.

Unlike the main website repository, docs do not use a root uv workspace. Run
``uv`` commands from inside the ``backend`` folder.