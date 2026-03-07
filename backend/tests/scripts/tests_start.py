import subprocess
import sys


def main() -> None:
    # python app/tests_pre_start.py
    subprocess.run([sys.executable, "app/tests_pre_start.py"], check=True)

    # bash scripts/test.sh "$@"
    # Assuming scripts/test.sh is also being converted to Python, we'll call that if needed.
    # However, the original script calls scripts/test.sh.
    # Let's see if scripts/test.sh exists in the project.
    subprocess.run([sys.executable, "tests/scripts/test.py"] + sys.argv[1:], check=True)


if __name__ == "__main__":
    main()
