import pathlib
from collections import defaultdict

# ANSI Color Codes
GREEN = "\033[92m"
BLUE = "\033[94m"
BOLD = "\033[1m"
END = "\033[0m"

def main():
    schema_map = defaultdict(list)

    # Group files by their header string
    for path in pathlib.Path().glob("*.txt"):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                header = f.readline().strip()
                if header:
                    # Clean up tabs for display
                    clean_schema = header.replace('\t', ', ')
                    schema_map[clean_schema].append(path.name)
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
            print(f"  {BLUE}↳ {file}{END}")
        print() # Newline for spacing

if __name__ == "__main__":
    main()
