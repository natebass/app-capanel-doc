import platform
import subprocess
import sys
from pathlib import Path


def main() -> None:
    backend_dir = Path(__file__).resolve().parents[2]
    project_dir = backend_dir.parent
    compose_file = project_dir / "compose.yml"
    compose_cmd = ["docker-compose", "-f", str(compose_file)]

    # docker-compose down -v --remove-orphans
    subprocess.run(
        [*compose_cmd, "down", "-v", "--remove-orphans"],
        check=True,
        cwd=project_dir,
    )

    if platform.system() == "Linux":
        print("Remove __pycache__ files")
        # sudo find . -type d -name __pycache__ -exec rm -r {} \+
        # Avoid sudo unless necessary. Original used sudo, let's keep it if we can't find a better way.
        subprocess.run(
            [
                "sudo",
                "find",
                ".",
                "-type",
                "d",
                "-name",
                "__pycache__",
                "-exec",
                "rm",
                "-r",
                "{}",
                "+",
            ],
            check=True,
        )

    # docker-compose build
    subprocess.run([*compose_cmd, "build"], check=True, cwd=project_dir)

    # docker-compose up -d
    subprocess.run([*compose_cmd, "up", "-d"], check=True, cwd=project_dir)

    # docker-compose exec -T backend bash scripts/tests-start.sh "$@"
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


if __name__ == "__main__":
    main()
