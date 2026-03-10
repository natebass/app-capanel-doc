import subprocess
import sys
from pathlib import Path


def main() -> None:
    backend_dir = Path(__file__).resolve().parents[2]
    project_dir = backend_dir.parent
    compose_file = project_dir / "compose.yml"
    compose_cmd = ["docker", "compose", "-f", str(compose_file)]

    try:
        # docker compose build
        subprocess.run([*compose_cmd, "build"], check=True, cwd=project_dir)

        # docker compose down -v --remove-orphans
        subprocess.run(
            [*compose_cmd, "down", "-v", "--remove-orphans"],
            check=True,
            cwd=project_dir,
        )

        # docker compose up -d
        subprocess.run([*compose_cmd, "up", "-d"], check=True, cwd=project_dir)

        # docker compose exec -T backend bash scripts/tests-start.sh "$@"
        # We assume the Python version should be called inside the container, but since we are converting,
        # it might need adjustment if the image expects bash.
        # However, let's stick to calling the Python script if we have it inside the container too.
        # Assuming the container has Python installed.
        subprocess.run(
            [
                *compose_cmd,
                "exec",
                "-T",
                "backend",
                "python",
                "tests/scripts/tests_start.py",
            ]
            + sys.argv[1:],
            check=True,
            cwd=project_dir,
        )

    finally:
        # docker compose down -v --remove-orphans
        subprocess.run(
            [*compose_cmd, "down", "-v", "--remove-orphans"],
            check=True,
            cwd=project_dir,
        )


if __name__ == "__main__":
    main()
