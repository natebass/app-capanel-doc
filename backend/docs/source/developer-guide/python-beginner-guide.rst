.. role:: python(code)
   :language: python

.. role:: bash(code)
   :language: bash

.. default-role:: strong

==================================================
Python Beginner's Guide - FastAPI Backend Setup
==================================================

.. contents:: Table of Contents
   :depth: 2
   :local:

.. _what-is-python-fastapi:

What is Python & FastAPI?
********************************************
Python
=========================================================
**Python** is a high-level, easy-to-read programming language that's perfect for beginners. It's used for web development, data analysis, artificial intelligence, and more.

FastAPI
=========================================================
**FastAPI** is a modern web framework for building APIs (Application Programming Interfaces) with Python. It's:

* Fast to write and fast to run
* Automatically generates API documentation
* Has built-in validation and type checking

Our Tech Stack
=========================================================

* **FastAPI**: Web framework for building the API
* **SQLModel**: Database models and queries (built on SQLAlchemy + Pydantic)
* **Celery**: Background task processing
* **Redis**: In-memory database for caching and task queues
* **PostgreSQL**: Main database for storing data
* **Docker**: Containerization for easy deployment
* **uv**: Modern Python package manager

.. _prerequisites:

Prerequisites
********************************************
Required Software
=========================================================

1.  **Docker Desktop**: `Download here <https://www.docker.com/products/docker-desktop/>`_
2.  **Python 3.12+**: `Download here <https://www.python.org/downloads/>`_
3.  **uv Package Manager**: `Installation guide <https://docs.astral.sh/uv/>`_
4.  **Git**: `Download here <https://git-scm.com/downloads>`_
5.  **Visual Studio Code**: `Download here <https://code.visualstudio.com/>`_ (recommended editor)

VS Code Extensions (Recommended)
=========================================================

* Python extension by Microsoft
* Python Debugger
* Docker extension
* Thunder Client (for API testing)

.. _setting-up-your-development-environment:

Setting Up Your Development Environment
********************************************

Step 1: Clone the Repository
=========================================================

.. code-block:: bash

    # Navigate to your desired directory
    cd "C:\Users\shwnd\Desktop\LB_LocalCopy\Coding"

    # Clone the project (if not already done)
    git clone <your-repository-url> app-capanel-web
    cd app-capanel-web

Step 2: Install uv (Python Package Manager)
=========================================================

.. code-block:: bash

    # On Windows (PowerShell)
    irm https://astral.sh/uv/install.ps1 | iex

    # On macOS/Linux
    curl -LsSf https://astral.sh/uv/install.sh | sh

Step 3: Set Up the Backend Environment
=========================================================

.. code-block:: bash

    # Navigate to the backend directory
    cd backend

    # Install all Python dependencies
    uv sync

    # Activate the virtual environment
    # On Windows:
    .venv\Scripts\activate

    # On macOS/Linux:
    source .venv/bin/activate

Step 4: Start the Development Environment
=========================================================

.. code-block:: bash

    # Go back to the root directory
    cd ..

    # Start all services with Docker Compose
    docker compose up -d

    # Watch for changes (recommended during development)
    docker compose watch

Step 5: Verify Everything Works
=========================================================

1.  Open your browser and go to ``http://localhost/docs``
2.  You should see the FastAPI automatic documentation (Swagger UI)
3.  Try the "Hello World" endpoint to make sure it's working

.. _understanding-the-project-structure:

Understanding the Project Structure
********************************************

.. code-block::
    
    backend/
    ├── app/                          # Main application code
    │   ├── api/                      # API endpoints
    │   │   └── routes/               # Individual route files
    │   │       ├── census.py         # Census data endpoints
    │   │       ├── items.py          # Items endpoints
    │   │       ├── login.py          # Authentication endpoints
    │   │       └── users.py          # User management endpoints
    │   ├── core/                     # Core configuration
    │   │   ├── config.py             # App settings
    │   │   ├── db.py                 # Database connection
    │   │   └── security.py          # Security utilities
    │   ├── crud/                     # Database operations
    │   │   ├── crud_census.py        # Census data CRUD
    │   │   ├── crud_item.py          # Items CRUD
    │   │   └── crud_user.py          # User CRUD
    │   ├── models/                   # Database models
    │   │   └── models.py             # SQLModel definitions
    │   ├── tests/                    # Unit tests
    │   └── main.py                   # Application entry point
    ├── alembic/                      # Database migrations
    ├── scripts/                      # Utility scripts
    └── pyproject.toml               # Python dependencies and config

.. _working-with-the-census-data-api:

Working with the Census Data API
********************************************

Understanding the Census Data Flow
=========================================================

1.  **Database Model** (``app/models/models.py``):

    .. code-block:: python

        class CensusData(SQLModel, table=True):
            id: int | None = Field(default=None, primary_key=True)
            school_name: str
            total_enr: int  # This is what the frontend displays
            academic_year: str
            charter: str
            # ... other fields

2.  **CRUD Operations** (``app/crud/crud_census.py``):

    .. code-block:: python

        def get_total_enrollment(db: Session) -> int:
            """Calculate total enrollment across all schools"""
            result = db.exec(select(func.sum(CensusData.total_enr))).first()
            return result or 0

3.  **API Endpoint** (``app/api/routes/census.py``):

    .. code-block:: python

        @router.get("/censusdata")
        def get_census_data(db: Session = Depends(get_db)):
            """Get census data for the dashboard"""
            total = get_total_enrollment(db)
            return {
                "data": {"total_enr": total},
                "status": "success"
            }

The Complete Data Journey
=========================================================

1.  **Database**: PostgreSQL stores the census records
2.  **CRUD Function**: Calculates the total enrollment sum
3.  **API Endpoint**: Returns the data in JSON format
4.  **Frontend**: Fetches and displays the data

.. _step-by-step-tutorial:

Step-by-Step Tutorial
********************************************

Tutorial 1: Adding a New Field to Census Data
=========================================================

Let's add a ``district_name`` field to our census data.

Step 1: Update the Database Model
----------------------------------------------------------

.. code-block:: python

    # In app/models/models.py
    class CensusData(SQLModel, table=True):
        id: int | None = Field(default=None, primary_key=True)
        school_name: str
        district_name: str  # ← Add this new field
        total_enr: int
        academic_year: str
        charter: str
        # ... other existing fields

Step 2: Create a Database Migration
----------------------------------------------------------

.. code-block:: bash

    # Make sure you're in the backend directory and virtual env is active
    cd backend

    # Create a new migration
    docker compose exec backend bash
    alembic revision --autogenerate -m "Add district_name to CensusData"

    # Apply the migration
    alembic upgrade head

Step 3: Update the CRUD Function
----------------------------------------------------------

.. code-block:: python

    # In app/crud/crud_census.py
    def get_census_by_district(db: Session, district_name: str) -> list[CensusData]:
        """Get all census data for a specific district"""
        statement = select(CensusData).where(CensusData.district_name == district_name)
        return db.exec(statement).all()

Step 4: Add a New API Endpoint
----------------------------------------------------------

.. code-block:: python

    # In app/api/routes/census.py
    @router.get("/censusdata/district/{district_name}")
    def get_district_census_data(
        district_name: str,
        db: Session = Depends(get_db)
    ):
        """Get census data for a specific district"""
        data = get_census_by_district(db, district_name)
        if not data:
            raise HTTPException(status_code=404, detail="District not found")
        
        return {
            "data": [school.model_dump() for school in data],
            "status": "success"
        }

Tutorial 2: Creating a New API Endpoint from Scratch
=========================================================

Let's create an endpoint to get the average enrollment per district.

Step 1: Create the CRUD Function
----------------------------------------------------------

.. code-block:: python

    # In app/crud/crud_census.py
    def get_average_enrollment_by_district(db: Session) -> list[dict]:
        """Calculate average enrollment by district"""
        statement = (
            select(
                CensusData.district_name,
                func.avg(CensusData.total_enr).label("avg_enrollment"),
                func.count(CensusData.id).label("school_count")
            )
            .group_by(CensusData.district_name)
            .order_by(func.avg(CensusData.total_enr).desc())
        )
        
        results = db.exec(statement).all()
        return [
            {
                "district_name": row[0],
                "average_enrollment": round(float(row[1]), 2),
                "school_count": row[2]
            }
            for row in results
        ]

Step 2: Create the API Endpoint
----------------------------------------------------------

.. code-block:: python

    # In app/api/routes/census.py
    @router.get("/censusdata/districts/averages")
    def get_district_averages(db: Session = Depends(get_db)):
        """Get average enrollment by district"""
        try:
            data = get_average_enrollment_by_district(db)
            return {
                "data": data,
                "status": "success",
                "count": len(data)
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error calculating district averages: {str(e)}"
            )

Step 3: Test Your New Endpoint
----------------------------------------------------------

1.  Start your development server: ``docker compose watch``
2.  Go to ``http://localhost/docs``
3.  Find your new endpoint in the documentation
4.  Click "Try it out" and test it

.. _common-python-concepts:

Common Python Concepts
********************************************

1. Type Hints
=========================================================

.. code-block:: python

    # Type hints help catch errors and make code clearer
    def calculate_total(numbers: list[int]) -> int:
        return sum(numbers)

    # Optional types
    def get_user_name(user_id: int) -> str | None:
        # Returns either a string or None
        pass

2. List Comprehensions
=========================================================

.. code-block:: python

    # Instead of:
    results = []
    for item in data:
        if item.is_active:
            results.append(item.name)

    # You can write:
    results = [item.name for item in data if item.is_active]

3. Dictionary Operations
=========================================================

.. code-block:: python

    # Creating dictionaries
    user_data = {
        "name": "John Doe",
        "email": "john@example.com",
        "age": 30
    }

    # Safe access with .get()
    email = user_data.get("email", "no-email@example.com")  # Provides default

4. Error Handling
=========================================================

.. code-block:: python

    try:
        result = risky_operation()
        return {"data": result, "status": "success"}
    except ValueError as e:
        # Handle specific error types
        raise HTTPException(status_code=400, detail=f"Invalid data: {e}")
    except Exception as e:
        # Handle any other errors
        raise HTTPException(status_code=500, detail=f"Server error: {e}")

5. Working with Databases
=========================================================

.. code-block:: python

    # SQLModel/SQLAlchemy patterns
    from sqlmodel import Session, select

    def get_items_by_user(db: Session, user_id: int):
        # Create a query
        statement = select(Item).where(Item.user_id == user_id)
        
        # Execute and get results
        items = db.exec(statement).all()
        return items

.. _debugging-and-troubleshooting:

Debugging and Troubleshooting
********************************************

Common Error Messages and Solutions
=========================================================

1. "ModuleNotFoundError: No module named 'xxx'"
----------------------------------------------------------

**Problem**: A Python package is not installed.

.. code-block:: bash

    # Solution: Install the missing package
    uv add package-name

    # Or sync all dependencies
    uv sync

2. "ImportError: attempted relative import with no known parent package"
------------------------------------------------------------------------

**Problem**: Python can't find your modules.

.. code-block:: bash

    # Solution: Make sure you're running from the correct directory
    cd backend
    python -m app.main  # Use module syntax

3. Database Connection Errors
----------------------------------------------------------

**Problem**: Can't connect to the database.

.. code-block:: bash

    # Solution: Make sure Docker services are running
    docker compose up -d

    # Check if database is ready
    docker compose logs db

4. "uvicorn command not found"
----------------------------------------------------------

**Problem**: Virtual environment is not activated.

.. code-block:: bash

    # Solution: Activate the virtual environment
    # Windows:
    .venv\Scripts\activate

    # macOS/Linux:
    source .venv/bin/activate

Debugging Tools
=========================================================

1. Print Debugging
----------------------------------------------------------

.. code-block:: python

    def my_function(data):
        print(f"Input data: {data}")  # Debug print
        result = process_data(data)
        print(f"Processed result: {result}")  # Debug print
        return result

2. Python Debugger (pdb)
----------------------------------------------------------

.. code-block:: python

    import pdb

    def problematic_function():
        some_code()
        pdb.set_trace()  # Execution will pause here
        more_code()

3. FastAPI Error Details
----------------------------------------------------------

FastAPI automatically provides detailed error messages. Check:

* Browser console for frontend errors
* Terminal logs for backend errors
* ``http://localhost/docs`` for API documentation

4. Docker Logs
----------------------------------------------------------

.. code-block:: bash

    # View logs for all services
    docker compose logs

    # View logs for specific service
    docker compose logs backend

    # Follow logs in real-time
    docker compose logs -f backend

Testing Your APIs
=========================================================

1. Using the Browser
----------------------------------------------------------

* Go to ``http://localhost/docs`` for interactive documentation
* Test endpoints directly in the browser

2. Using curl
----------------------------------------------------------

.. code-block:: bash

    # Test GET endpoint
    curl http://localhost/api/v1/censusdata

    # Test POST endpoint with JSON data
    curl -X POST http://localhost/api/v1/items \
      -H "Content-Type: application/json" \
      -d '{"title": "Test Item", "description": "Test description"}'

3. Using Python requests
----------------------------------------------------------

.. code-block:: python

    import requests

    # Test your API from Python
    response = requests.get("http://localhost/api/v1/censusdata")
    print(response.json())

.. _next-steps:

Next Steps
********************************************

1. Learn More Python
=========================================================

* **Official Python Tutorial**: `https://docs.python.org/3/tutorial/ <https://docs.python.org/3/tutorial/>`_
* **Automate the Boring Stuff**: `https://automatetheboringstuff.com/ <https://automatetheboringstuff.com/>`_
* **Python Crash Course**: Great book for beginners

2. FastAPI Deep Dive
=========================================================

* **FastAPI Tutorial**: `https://fastapi.tiangolo.com/tutorial/ <https://fastapi.tiangolo.com/tutorial/>`_
* **SQLModel Tutorial**: `https://sqlmodel.tiangolo.com/tutorial/ <https://sqlmodel.tiangolo.com/tutorial/>`_
* **Advanced FastAPI**: Dependency injection, middleware, background tasks

3. Database Skills
=========================================================

* **SQL Basics**: Learn SELECT, INSERT, UPDATE, DELETE
* **PostgreSQL Documentation**: `https://www.postgresql.org/docs/ <https://www.postgresql.org/docs/>`_
* **Database Design**: Normalization, relationships, indexes

4. Testing
=========================================================

.. code-block:: python

    # Example test for your API
    import pytest
    from fastapi.testclient import TestClient
    from app.main import app

    client = TestClient(app)

    def test_get_census_data():
        response = client.get("/api/v1/censusdata")
        assert response.status_code == 200
        assert "data" in response.json()

5. Production Deployment
=========================================================

* Learn about Docker containers
* Environment variables and configuration
* Database migrations
* Monitoring and logging

Helpful Commands Reference
********************************************

Python/uv Commands
=========================================================

.. code-block:: bash

    # Create new virtual environment
    uv venv

    # Install dependencies
    uv sync

    # Add new package
    uv add package-name

    # Remove package
    uv remove package-name

    # Run Python script
    uv run python script.py

    # Activate virtual environment
    source .venv/bin/activate    # macOS/Linux
    .venv\Scripts\activate       # Windows

Docker Commands
=========================================================

.. code-block:: bash

    # Start all services
    docker compose up -d

    # Watch for changes during development
    docker compose watch

    # View logs
    docker compose logs backend

    # Execute command in running container
    docker compose exec backend bash

    # Stop all services
    docker compose down

    # Clean up (removes data!)
    docker compose down -v

Database Commands
=========================================================

.. code-block:: bash

    # Create new migration
    alembic revision --autogenerate -m "Description of changes"

    # Apply migrations
    alembic upgrade head

    # View migration history
    alembic history

    # Rollback one migration
    alembic downgrade -1

## Getting Help

Resources
=========================================================

1.  **Project Documentation**: Read the README files in each directory
2.  **FastAPI Docs**: `https://fastapi.tiangolo.com/ <https://fastapi.tiangolo.com/>`_
3.  **Python Docs**: `https://docs.python.org/3/ <https://docs.python.org/3/>`_
4.  **Stack Overflow**: Search for specific error messages
5.  **GitHub Issues**: Check if others have had similar problems

When Asking for Help
=========================================================

1.  Include the full error message
2.  Describe what you were trying to do
3.  Share the relevant code
4.  Mention your operating system and Python version

Remember: Everyone starts as a beginner! Take your time, read error messages carefully, and don't be afraid to experiment. The best way to learn programming is by doing.