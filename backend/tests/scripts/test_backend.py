import subprocess
import sys


def main() -> None:
    coverage_title = (
        f"{' '.join(sys.argv[1:])}-coverage" if sys.argv[1:] else "backend-coverage"
    )

    # coverage run -m pytest tests/
    subprocess.run(["coverage", "run", "-m", "pytest", "tests/"], check=True)

    # coverage report
    subprocess.run(["coverage", "report"], check=True)

    # coverage html --title "${@-coverage}"
    subprocess.run(["coverage", "html", "--title", coverage_title], check=True)


if __name__ == "__main__":
    main()
