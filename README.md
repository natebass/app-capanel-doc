# California Accountability Panel documentation

Documentation for the California Accountability Panel website. https://github.com/opensacorg/app-capanel-web

The general application and Python documentation uses Sphinx. This is where most of the documentation should be. For more information, see the [Sphinx documentation](https://opensacorg.github.io/app-capanel-doc/developer-guide/sphinx). The frontend documentation uses [Storybook](https://opensacorg.github.io/app-capanel-doc/developer-guide/storybook).

## Documentation vs. Application (Separate Repositories)

**Important:** This is the **documentation repository only**. The actual web application is in a **separate repository**.



### Key Differences

- 📚 **app-capanel-doc** = Documentation website (Sphinx-generated HTML pages)
- ✅ **app-capanel-web** = The actual application (FastAPI backend + React frontend)
- 🔄 They are **completely separate** and do not depend on each other
- 📖 Running the documentation does **NOT** run the web app
- 🚀 Running the web app does **NOT** run the documentation

### Running the Web Application

To run the actual California Accountability Panel application:

```powershell
cd C:\Users\Shawn\Desktop\GCC_AI\app-capanel-web
docker compose up
```

For more details, see: [app-capanel-web/README.md](https://github.com/opensacorg/app-capanel-web)

### Running Both Documentation and Application

To run both simultaneously, use **two separate terminals**:

**Terminal 1 - Documentation (this repo):**
```powershell
cd C:\Users\Shawn\Desktop\GCC_AI\app-capanel-doc\backend\docs\build\html
python -m http.server 8000
```
Then open: http://localhost:8000

**Terminal 2 - Web Application:**
```powershell
cd C:\Users\Shawn\Desktop\GCC_AI\app-capanel-web
docker compose up
```

## Prerequisites

- [uv](https://docs.astral.sh/uv/) - Python package manager (v0.9.7+)
- [pnpm](https://pnpm.io/) - Node.js package manager (v9.12.3+)
- [Make](https://opensacorg.github.io/app-capanel-doc/developer_guide#install) - Build automation tool (GNU Make 3.81+)
- Python 3.13+ (managed by uv)

### Verify Prerequisites

Before starting, verify all tools are installed:

```powershell
# Check uv installation
uv --version
# Expected: uv 0.9.7 or higher

# Check pnpm installation
pnpm --version
# Expected: 9.12.3 or higher

# Check make installation
make --version
# Expected: GNU Make 3.81 or higher
```

## Quickstart

This project supports VSCode and Make. **If you have any issues with these commands, try to run the corresponding application individually with uv or pnpm.** 

### Create an `.env` file.

To run the main FastAPI application, first create an `.env` file in the root of the repository. For all of the options, see the [environment variable documentation](https://opensacorg.github.io/app-capanel-doc/developer-guide/environment-variable). This step can be skipped if you just want to build/run the documentation.

```dotenv
FIRST_SUPERUSER=admin@example.com
FIRST_SUPERUSER_PASSWORD=changethis
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
```

### Boot Up Documentation (Step-by-Step)

#### Method 1: Quick Start (Recommended for Viewing Docs)

**Step 1: Navigate to the project directory**
```powershell
cd C:\Users\Shawn\Desktop\GCC_AI\app-capanel-doc
```

**Step 2: Sync Python dependencies**
```powershell
cd backend
uv sync
```

This command:
- Reads `pyproject.toml` and `uv.lock`
- Installs all required Python packages into `.venv`
- Ensures you have Sphinx and all extensions

**Step 3: Install missing Sphinx extension (if needed)**
```powershell
uv add sphinxcontrib-mermaid
```

**Step 4: Build the HTML documentation**
```powershell
cd docs
uv run sphinx-build -b html source build/html
```

This command:
- Runs Sphinx to build HTML from `.rst` and `.md` files
- Outputs to `backend/docs/build/html/`
- You may see some warnings (missing toctree references) - these are non-critical

**Step 5: Start a local web server**

**Option A: Auto-Reload Server (Recommended for Development)**
```powershell
uv run sphinx-autobuild source build/html --open-browser
```
This will:
- ✨ Automatically rebuild when you save changes to source files
- 🔄 Auto-refresh your browser when rebuilds complete
- 🌐 Open http://127.0.0.1:8000 automatically

**Option B: Simple HTTP Server (View Only)**
```powershell
cd build/html
python -m http.server 8000
```
This serves static files but does **NOT** auto-reload on changes.

**Step 6: Open your browser**

Navigate to: http://localhost:8000 (or http://127.0.0.1:8000 for auto-reload)

You should now see the documentation website! 🎉

**To stop the server:** Press `Ctrl+C` in the terminal

#### Method 2: Using Make (Production Build)

⚠️ **Note:** The Makefile in the root directory has issues with the `reload` target. Use the backend-specific commands instead.

**From the project root:**
```powershell
# Build HTML documentation (one-time build)
cd backend/docs
make html

# Preview the documentation
make preview
```

### VSCode

Enable the workspace recommended extensions before running a launch command. For all of the options, see the [VSCode support documentation](https://opensacorg.github.io/app-capanel-doc/developer-guide/vscode)

- Run the frontend and backend application.

### Make

For all of the options, see the [Make support documentation](https://opensacorg.github.io/app-capanel-doc/developer-guide/vscode)

#### Build and launch the Sphinx documentation.

Live-reload the backend documentation and start a local server on [localhost:8000](localhost:8000).

```shell
cd backend/docs
make reload
```

You can also use:

```shell
cd backend/docs
make html
make preview
```

#### Build and launch the Storybook documentation.

```shell
make storybook
```

## Troubleshooting

### Common Issues

**Issue 1: `sphinxcontrib.mermaid` not found**
```
Solution: Run `uv add sphinxcontrib-mermaid` from the backend directory
```

**Issue 2: `make: *** No rule to make target 'reload'. Stop.`**
```
Solution: Use the backend-specific Makefile instead:
cd backend/docs
make reload
```

**Issue 3: `sphinx-build command not found`**
```
Solution: Use `uv run sphinx-build` instead of calling sphinx-build directly
```

**Issue 4: Port 8000 already in use**
```
Solution: Use a different port:
python -m http.server 8001
```

## Development Workflow

1. **Make changes** to documentation files in `backend/docs/source/`
2. **Rebuild** the documentation: `uv run sphinx-build -b html source build/html`
3. **Refresh** your browser to see changes
4. **Repeat** as needed

For live-reload during development, use:
```powershell
cd backend/docs
make reload
```

## Project Structure

```
app-capanel-doc/
├── backend/
│   ├── docs/
│   │   ├── source/        # Documentation source files (.rst, .md)
│   │   ├── build/         # Generated HTML (git-ignored)
│   │   └── Makefile       # Backend-specific build commands
│   ├── app/               # FastAPI application code
│   ├── pyproject.toml     # Python dependencies
│   └── .venv/             # Virtual environment (auto-created by uv)
├── frontend/
│   └── ...                # Storybook documentation
└── README.md              # This file
```

## Contribute

You can get involved by joining our Meetup group and Slack channel. For more information on contributing to the project, see the [contribution guide](https://opensacorg.github.io/app-capanel-doc/contribute).
