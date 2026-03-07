import platform
import subprocess
import sys


def main() -> None:
    # docker-compose down -v --remove-orphans
    subprocess.run(["docker-compose", "down", "-v", "--remove-orphans"], check=True)

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
    subprocess.run(["docker-compose", "build"], check=True)

    # docker-compose up -d
    subprocess.run(["docker-compose", "up", "-d"], check=True)

    # docker-compose exec -T backend bash scripts/tests-start.sh "$@"
    subprocess.run(
        [
            "docker-compose",
            "exec",
            "-T",
            "backend",
            "python",
            "tests/scripts/tests_start.py",
        ]
        + sys.argv[1:],
        check=True,
    )


if __name__ == "__main__":
    main()
