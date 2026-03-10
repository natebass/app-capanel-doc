from __future__ import annotations

from app.scripts.gcp.gcp_utils import ScriptError, compute_paths, run_command


def main() -> int:
    """
    Generate OpenAPI client for the frontend.
    """
    paths = compute_paths(__file__)
    backend_dir = paths.backend_dir
    repo_dir = paths.repo_dir
    frontend_dir = repo_dir / "frontend"

    output_file = repo_dir / "openapi.json"

    openapi = run_command(
        [
            "python",
            "-c",
            "import app.main, json; print(json.dumps(app.main.app.openapi()))",
        ],
        cwd=backend_dir,
        capture_output=True,
    )
    output_file.write_text(openapi.stdout)

    frontend_openapi = frontend_dir / "openapi.json"
    output_file.replace(frontend_openapi)

    run_command(["pnpm", "run", "openapi-ts"], cwd=frontend_dir)
    run_command(["pnpx", "oxfmt"], cwd=frontend_dir)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ScriptError as exc:
        raise SystemExit(str(exc)) from exc
