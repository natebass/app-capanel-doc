import subprocess
import sys


def main() -> None:
    try:
        # docker compose build
        subprocess.run(["docker", "compose", "build"], check=True)

        # docker compose down -v --remove-orphans
        subprocess.run(
            ["docker", "compose", "down", "-v", "--remove-orphans"], check=True
        )

        # docker compose up -d
        subprocess.run(["docker", "compose", "up", "-d"], check=True)

        # docker compose exec -T backend bash scripts/tests-start.sh "$@"
        # We assume the Python version should be called inside the container, but since we are converting,
        # it might need adjustment if the image expects bash.
        # However, let's stick to calling the Python script if we have it inside the container too.
        # Assuming the container has Python installed.
        subprocess.run(
            [
                "docker",
                "compose",
                "exec",
                "-T",
                "backend",
                "python",
                "tests/scripts/tests_start.py",
            ]
            + sys.argv[1:],
            check=True,
        )

    finally:
        # docker compose down -v --remove-orphans
        subprocess.run(
            ["docker", "compose", "down", "-v", "--remove-orphans"], check=True
        )


if __name__ == "__main__":
    main()
