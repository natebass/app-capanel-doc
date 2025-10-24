 Documentation
=========================================

Sphinx documentation for the California Accountability Panel web application.

Building Documentation
-----------------

The documentation build process uses the uv-managed virtual environment in `backend/.venv` to ensure consistent dependencies.

Quick Start
-----------------

From the `backend/docs` directory:
cd backend/docs
make html

Available Targets
-----------------

- `make html` - Build HTML documentation
- `make preview` - Build HTML documentation and open in browser
- `make reload` - Live reload the changes on a local server
- `make clean` - Clean build artifacts
- `make help` - Show available Sphinx build targets

How It Works
-----------------

The Makefile automatically:
1. Ensures the uv virtual environment exists at `backend/.venv`
2. Syncs all dependencies defined in `backend/pyproject.toml` (including Sphinx)
3. Sets up the correct PYTHONPATH for autodoc to import the application code
4. Runs Sphinx using the managed Python interpreter

Viewing Documentation
-----------------

After building, open the generated documentation:
xdg-open build/html/index.html

Makefile Targets for Sphinx Documentation
=========================================

This Makefile automates Sphinx documentation workflows using a uv-managed Python environment.

Environment Setup
-----------------

- **PROJECT_ROOT**: Absolute path to the project root.
- **VENV_DIR**: Virtual environment directory (`.venv`).
- **UV**: Package manager (default: `uv`).
- **PYTHON**: Platform-specific Python executable path.
- **SET_PYTHONPATH**: Ensures `PYTHONPATH` includes the project root.

Sphinx Configuration
--------------------

- **SOURCE_DIRECTORY**: Location of Sphinx source files (`source`).
- **BUILD_DIR**: Output directory for builds (`build`).
- **SPHINX_OPTIONS**: Optional flags passed to Sphinx.
- **SPHINX_BUILD**: Command to invoke Sphinx with the correct `PYTHONPATH`.

Make Targets
------------

- ``help``: Displays available Sphinx targets.
- ``docs-deps``: Creates `.venv` and installs dependencies via uv.
- ``clean``: Removes all files in the build directory.
- ``html``: Builds HTML documentation.
- ``preview``: Opens the HTML output in the default browser.
- ``reload``: Starts `sphinx-autobuild` for live preview.
- ``%``: Routes unknown targets to Sphinx's `make mode`.

Platform Behavior
-----------------

- On **Windows**, uses `Scripts/python.exe` and `set PYTHONPATH`.
- On **Unix/macOS**, uses `bin/python` and `PYTHONPATH=...`.

Usage
-----

To build HTML documentation:

.. code-block:: bash

   make html

To preview in browser:

.. code-block:: bash

   make preview

To clean build artifacts:

.. code-block:: bash

   make clean

To install dependencies:

.. code-block:: bash

   make docs-deps

To use Sphinx's built-in targets:

.. code-block:: bash

   make <target>  # e.g., make latexpdf


California Accountability Panel Documentation Configuration
===========================================================

General Configuration
---------------------
- **Extensions**:
  - `sphinx.ext.autodoc`
  - `sphinx_autodoc_typehints`

- **Templates Path**: `_templates`
- **Exclude Patterns**: None

- Add options to enable the "Edit on GitHub" button.

HTML Output Options
-------------------
- **Theme**: `pydata_sphinx_theme`
- **Static Path**: `_static`
- **Favicon**: `_static/image/favicon.ico`

- **Theme Options**:
  - Collapse navigation: False
  - Sticky navigation: True
  - Navigation depth: 4
  - Include hidden: True
  - Titles only: False
  - Use edit page button: True
  - Navbar alignment: Right
