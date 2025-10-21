"""
check_table.py

Checks if the 'censusdata' table exists in the database and lists all tables.

Syntax:
    python check_table.py

How to use:
1. Ensure your database URI is set in app.core.config.settings.SQLALCHEMY_DATABASE_URI.
2. Run this script from the command line:
       python check_table.py
3. The script will print whether the 'censusdata' table exists and list all tables in the database.
"""

from sqlmodel import create_engine, text

from app.core.config import settings

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))

with engine.connect() as conn:
    # Check if censusdata table exists
    result = conn.execute(
        text(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'censusdata';"
        )
    ).fetchall()

    print(f"Does 'censusdata' table exist: {len(result) > 0}")
    print(f'Tables found: {result}')

    # List all tables
    all_tables = conn.execute(
        text(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';"
        )
    ).fetchall()
    print('All tables in the database:')
    if not all_tables:
        print('  - No tables found.')
    else:
        print('  - Tables found:')
    for (table_name,) in all_tables:
        print(f'  - {table_name}')
