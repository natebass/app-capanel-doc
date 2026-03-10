import subprocess
import sys


def main() -> None:
    # python tests/scripts/tests_pre_start.py
    subprocess.run([sys.executable, "tests/scripts/tests_pre_start.py"], check=True)

    # /app/scripts/tests-start.sh forwards args to pytest.
    # Match that behavior here for in-container execution.
    subprocess.run(["pytest"] + sys.argv[1:], check=True)


if __name__ == "__main__":
    main()
