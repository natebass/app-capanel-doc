from sqlalchemy import Engine
from sqlmodel import text

from app.core.database import engine
from app.scripts.gcp.gcp_utils import load_repo_env_if_present

load_repo_env_if_present(__file__, scope="check_table")


def init(db_engine: Engine) -> None:
    """
    Check if the 'censusdata' table exists in the database and lists all tables.

    Syntax:
        python check_table.py

    How to use:
    1. Ensure your database URI is set in app.core.config.settings.SQLALCHEMY_DATABASE_URI.
    2. Run this script from the command line:
           python check_table.py
    3. The script will print whether the 'censusdata' table exists and list all tables in the database.
    """
    with db_engine.connect() as conn:
        result = conn.execute(
            text(
                "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'censusdata';"
            )
        ).fetchall()
        print(f"Does 'censusdata' table exist: {len(result) > 0}")
        print(f"Tables found: {result}")
        all_tables = conn.execute(
            text(
                "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';"
            )
        ).fetchall()
        print("All tables in the database:")
        if not all_tables:
            print("  - No tables found.")
        else:
            print("  - Tables found:")
        for (table_name,) in all_tables:
            print(f"  - {table_name}")


def main() -> None:
    init(engine)


if __name__ == "__main__":
    main()
