from __future__ import annotations

from app.scripts.gcp_utils import ScriptError, log, run_command


def main() -> int:
    scope = "prestart"
    log(scope, "Waiting for database connection")
    run_command(["python", "app/scripts/backend_pre_start.py"])

    log(scope, "Running database migrations")
    run_command(["alembic", "upgrade", "head"])

    log(scope, "Creating initial data")
    run_command(["python", "app/scripts/initial_data.py"])

    log(scope, "Prestart tasks completed (no data imports)")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ScriptError as exc:
        raise SystemExit(str(exc)) from exc
