# Documentation

This directory contains Sphinx documentation for the California Accountability Panel web application.

## Building Documentation

The documentation build process uses the uv-managed virtual environment in `backend/.venv` to ensure consistent dependencies.

### Quick Start

From the `backend/docs` directory:

```bash
cd backend/docs
make html   # uses uv + backend/.venv
```

### Available Targets

- `make html` - Build HTML documentation
- `make preview` - Build HTML documentation and open in browser
- `make clean` - Clean build artifacts
- `make help` - Show available Sphinx build targets

### How It Works

The Makefile automatically:
1. Ensures the uv virtual environment exists at `backend/.venv`
2. Syncs all dependencies defined in `backend/pyproject.toml` (including Sphinx)
3. Sets up the correct PYTHONPATH for autodoc to import the application code
4. Runs Sphinx using the managed Python interpreter

### Fish Shell Compatibility

The build process works seamlessly with fish shell on Linux Mint. The Makefile uses absolute paths and doesn't rely on shell-specific features.

### Viewing Documentation

After building, open the generated documentation:

```bash
xdg-open build/html/index.html
```