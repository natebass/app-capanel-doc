import argparse
import pathlib
from collections import defaultdict

# ANSI Color Codes
GREEN = "\033[92m"
BLUE = "\033[94m"
BOLD = "\033[1m"
END = "\033[0m"


def main():
    """
    Get a summary of the schema of CAASPP files.
    """
    parser = argparse.ArgumentParser(description="Check schema of CAASPP files.")
    parser.add_argument(
        "paths",
        nargs="*",
        help="Files or directories to check. Defaults to current directory if not specified.",
    )
    args = parser.parse_args()

    paths_to_check = args.paths if args.paths else ["."]
    schema_map = defaultdict(list)
    files_to_process = []

    for path_str in paths_to_check:
        p = pathlib.Path(path_str)
        if p.is_dir():
            # If a folder(s) is specified, check for all txt files in that folder
            files_to_process.extend(p.glob("*.txt"))
        elif p.is_file():
            # If a file is specified, then parse the file(s)
            files_to_process.append(p)
        else:
            print(f"Warning: {path_str} is not a valid file or directory.")

    # Group files by their header string
    for path in files_to_process:
        try:
            with open(path, encoding="utf-8") as f:
                header = f.readline().strip()
                if header:
                    # Clean up tabs for display
                    clean_schema = header.replace("\t", ", ")
                    # Use the path as the display name
                    schema_map[clean_schema].append(str(path))
        except Exception:
            continue

    if not schema_map:
        print("No .txt files with content found.")
        return

    # Sort groups so those with the most files (matches) appear at the top
    sorted_groups = sorted(schema_map.items(), key=lambda x: len(x[1]), reverse=True)

    for schema, files in sorted_groups:
        print(f"{GREEN}{BOLD}SCHEMA:{END} {GREEN}{schema}{END}")
        for file in sorted(files):
            print(f"  {BLUE}-> {file}{END}")
        print()  # Newline for spacing


if __name__ == "__main__":
    main()
