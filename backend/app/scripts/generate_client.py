from __future__ import annotations

from app.scripts.script_utils import ScriptError, compute_paths, run_command


def main() -> int:
    """
    Generate OpenAPI client for the frontend.
    """
    paths = compute_paths(__file__)
    backend_dir = paths.backend_dir
    repo_dir = paths.repo_dir
    frontend_dir = repo_dir / "frontend"

    # Importing app.main builds Settings, which reads `.env` relative to the
    # working directory. This repository keeps a single one at the workspace
    # root; fall back to the backend directory for a checkout that keeps its
    # own there.
    env_dir = repo_dir if (repo_dir / ".env").is_file() else backend_dir

    output_file = repo_dir / "openapi.json"

    openapi = run_command(
        [
            "python",
            "-c",
            "import app.main, json; print(json.dumps(app.main.app.openapi()))",
        ],
        cwd=env_dir,
        capture_output=True,
    )
    output_file.write_text(openapi.stdout)

    frontend_openapi = frontend_dir / "openapi.json"
    output_file.replace(frontend_openapi)

    # openapi-ts 0.99.0 crashes on TypeScript 7, whose new ESM shape leaves
    # `ts.SyntaxKind` undefined at module load. `typescript` is one of its peer
    # dependencies, so pnpm satisfies it from whichever importer pulled the
    # generator in -- a `pkg>dep` override does not apply. The generator is
    # therefore a devDependency of the workspace root, alongside a pinned
    # TypeScript 5.9.3, while the front end stays on 7. Run the root's binary
    # against the config in `frontend`, whose paths are relative to it.
    run_command(
        ["openapi-ts"],
        cwd=frontend_dir,
        extra_candidates=[repo_dir / "node_modules" / ".bin" / "openapi-ts"],
    )
    # `vp fmt` reads the project's style from the `fmt` block in
    # frontend/vite.config.ts. A bare `oxfmt` finds no config, falls back to its
    # own defaults, and reformats the whole front end against the house style.
    run_command(
        ["pnpm", "--filter", "frontend", "exec", "vp", "fmt", "src/lib/client"],
        cwd=repo_dir,
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ScriptError as exc:
        raise SystemExit(str(exc)) from exc
