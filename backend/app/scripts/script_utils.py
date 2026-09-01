from __future__ import annotations

import os
import shlex
import shutil
import subprocess
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from string import Template


class ScriptError(RuntimeError):
    """Raised when script preconditions are not met."""


@dataclass(frozen=True)
class ScriptPaths:
    script_dir: Path
    backend_dir: Path
    repo_dir: Path


def compute_paths(current_file: str) -> ScriptPaths:
    resolved_file = Path(current_file).resolve()
    script_dir = resolved_file.parent

    backend_dir: Path | None = None
    for candidate in resolved_file.parents:
        if candidate.name != "backend":
            continue
        if (candidate / "app").is_dir():
            backend_dir = candidate
            break

    if backend_dir is None:
        # Fallback for unexpected layouts.
        backend_dir = script_dir.parents[2]

    repo_dir = backend_dir.parent
    return ScriptPaths(
        script_dir=script_dir, backend_dir=backend_dir, repo_dir=repo_dir
    )


def timestamp() -> str:
    return datetime.now(tz=UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def log(scope: str, message: str) -> None:
    print(f"[{timestamp()}] [{scope}] {message}", file=sys.stderr, flush=True)


def run_command(
    cmd: list[str],
    *,
    cwd: Path | None = None,
    env: Mapping[str, str] | None = None,
    check: bool = True,
    capture_output: bool = False,
    input_text: str | None = None,
    extra_candidates: Sequence[Path] = (),
) -> subprocess.CompletedProcess[str]:
    if not cmd:
        msg = "run_command received an empty command list"
        raise ScriptError(msg)

    resolved_cmd = [
        resolve_executable(cmd[0], extra_candidates=extra_candidates),
        *cmd[1:],
    ]
    print(f"+ {shlex.join(cmd)}", file=sys.stderr, flush=True)
    return subprocess.run(
        resolved_cmd,
        cwd=str(cwd) if cwd is not None else None,
        env=dict(env) if env is not None else None,
        check=check,
        text=True,
        capture_output=capture_output,
        input=input_text,
    )


def resolve_executable(
    executable: str, *, extra_candidates: Sequence[Path] = ()
) -> str:
    resolved = shutil.which(executable)
    if resolved:
        return resolved

    if os.name == "nt":
        # Some environments don't apply PATHEXT lookup consistently.
        for suffix in (".cmd", ".bat", ".exe"):
            resolved = shutil.which(f"{executable}{suffix}")
            if resolved:
                return resolved

    for candidate in extra_candidates:
        if candidate.is_file():
            return str(candidate)

    msg = (
        f"Executable not found: {executable}. Current PATH={os.environ.get('PATH', '')}"
    )
    raise ScriptError(msg)


def strip_wrapping_quotes(raw: str) -> str:
    if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in {'"', "'"}:
        return raw[1:-1]
    return raw


def parse_env_lines(content: str) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for line in content.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("export "):
            stripped = stripped[len("export ") :].strip()
        if "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        normalized_key = key.strip()
        normalized_value = strip_wrapping_quotes(value.strip())
        expanded = Template(normalized_value).safe_substitute(os.environ | parsed)
        parsed[normalized_key] = os.path.expanduser(expanded)
    return parsed


def load_env_file(path: Path, *, override: bool = True) -> dict[str, str]:
    values = parse_env_lines(path.read_text())
    for key, value in values.items():
        if override or key not in os.environ:
            os.environ[key] = value
    return values


def load_repo_env_if_present(
    current_file: str, *, override: bool = False, scope: str = "env"
) -> Path | None:
    repo_env = compute_paths(current_file).repo_dir / ".env"
    if not repo_env.is_file():
        log(scope, f"No repo .env found at {repo_env}; using existing environment.")
        return None
    load_env_file(repo_env, override=override)
    log(scope, f"Loaded environment from {repo_env}")
    return repo_env


def resolve_env_file(current_file: str, explicit_env_file: str | None) -> Path:
    if explicit_env_file:
        explicit_path = Path(explicit_env_file).expanduser().resolve()
        if explicit_path.is_file():
            return explicit_path
        msg = f"Environment file not found: {explicit_env_file}"
        raise ScriptError(msg)

    repo_env = compute_paths(current_file).repo_dir / ".env"
    if repo_env.is_file():
        return repo_env

    msg = (
        f"Environment file not found. Checked: {repo_env}. "
        "Pass an env file path as the first argument or create .env in the repo root."
    )
    raise ScriptError(msg)


def env_required(name: str, hint: str | None = None) -> str:
    value = os.environ.get(name, "")
    if value:
        return value
    suffix = f", {hint}" if hint else ""
    msg = f"Set {name}{suffix}"
    raise ScriptError(msg)


def env_or(name: str, default: str) -> str:
    value = os.environ.get(name)
    if value is None or value == "":
        return default
    return value


def env_bool(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "y", "on"}
