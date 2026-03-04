from __future__ import annotations

from app.scripts import prestart
from app.scripts.script_utils import ScriptError, log


def main() -> int:
    prestart.main()
    log(
        "prestart-with-data",
        "Prestart tasks completed (initial_data only; imports must be triggered manually)",
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ScriptError as exc:
        raise SystemExit(str(exc)) from exc
