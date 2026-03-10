import argparse
import subprocess
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[3]

MODES = {
    "full",
    "migrate_only",
    "initial_data",
    "import_ela_data",
    "import_indicators",
    "both_imports",
}


def _normalize_indicators_source(source: str) -> str:
    normalized = source.strip().lower().replace("_", "-")
    if normalized in {"state", "california-state", "california state"}:
        return "state"
    return "cde"


def _is_year_folder(name: str, year: str, source: str) -> bool:
    lowered = name.lower()
    if year not in lowered:
        return False
    if source == "cde":
        return "cde" in lowered
    return (
        "california-state" in lowered
        or "california_state" in lowered
        or ("california" in lowered and "state" in lowered)
    )


def _discover_indicator_paths(
    indicators_path: str | None, resources_path: str, years: list[str], source: str
) -> list[str]:
    base = (indicators_path or resources_path).strip()
    if not base:
        base = resources_path
    base_path = Path(base).expanduser()
    discovered: list[Path] = []

    def _get_year_folders(dir_path: Path, src: str) -> list[Path]:
        found: list[Path] = []
        if dir_path.is_dir():
            for child in sorted(dir_path.iterdir()):
                if not child.is_dir():
                    continue
                if any(_is_year_folder(child.name, year, src) for year in years):
                    found.append(child)
        return found

    # If the input already points to a year folder, use it directly.
    if any(_is_year_folder(base_path.name, year, source) for year in years):
        discovered = [base_path]
    elif base_path.is_dir():
        # Discover for the primary source
        discovered.extend(_get_year_folders(base_path, source))

        # If source is 'state', we also need 'cde' folders for indicators like CHRONIC
        if source == "state":
            discovered.extend(_get_year_folders(base_path, "cde"))

    if not discovered:
        sources = [source]
        if source == "state":
            sources.append("cde")

        for s in sources:
            prefix = "cde" if s == "cde" else "california-state"
            discovered.extend(
                [
                    Path(resources_path).expanduser() / f"{prefix}-{year}"
                    for year in years
                ]
            )

    # Deduplicate while preserving order.
    result: list[str] = []
    seen: set[str] = set()
    for path in discovered:
        p = str(path)
        if p in seen:
            continue
        seen.add(p)
        result.append(p)
    return result


def _discover_ela_files(resources_path: str, years: list[str]) -> list[str]:
    root = Path(resources_path).expanduser()
    discovered: list[str] = []
    seen: set[str] = set()

    for year in years:
        year_matches: list[Path] = []
        if root.exists():
            year_matches = sorted(
                p
                for p in root.rglob("*.xlsx")
                if p.is_file()
                and year in p.name.lower()
                and "ela" in p.name.lower()
                and "download" in p.name.lower()
                and "cde" in str(p.parent).lower()
            )

        if not year_matches:
            year_matches = [
                root / f"cde-{year}" / f"eladownload{year}.xlsx",
                root / "cde" / f"eladownload{year}.xlsx",
            ]

        for match in year_matches:
            path = str(match)
            if path in seen:
                continue
            seen.add(path)
            discovered.append(path)

    return discovered


def run_step(args: list[str], label: str) -> None:
    print(f"[pipeline] starting {label}: {' '.join(args)}", flush=True)
    subprocess.run([sys.executable, *args], check=True, cwd=BACKEND_DIR)
    print(f"[pipeline] finished {label}", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run backend import pipeline inside one Cloud Run job execution."
    )
    parser.add_argument("--mode", default="full", choices=sorted(MODES))
    parser.add_argument("--gcs-uri", default="gs://ca-panel-001-resources/resources")
    parser.add_argument("--resources-path", default="/tmp/resources")
    parser.add_argument("--ela-file", default=None)
    parser.add_argument("--ela-files", default="")
    parser.add_argument("--years", default="2024,2025")
    parser.add_argument("--indicators-source", default="cde")
    parser.add_argument("--indicators-path", default=None)
    parser.add_argument("--indicators-paths", default="")
    parser.add_argument("--batch-size", type=int, default=5000)
    parser.add_argument("--indicator", default="")
    parser.add_argument(
        "--skip-sync",
        action="store_true",
        help="Skip GCS sync and use only local resources already present at --resources-path.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing category rows (indicator + reporting year).",
    )
    args = parser.parse_args()

    if args.batch_size <= 0:
        raise ValueError("--batch-size must be > 0")

    resources_path = args.resources_path
    ela_file = args.ela_file or f"{resources_path}/cde/eladownload2025.xlsx"
    indicators_source = _normalize_indicators_source(args.indicators_source)
    indicators_path = args.indicators_path or resources_path

    years = [y.strip() for y in args.years.split(",") if y.strip()]
    explicit_ela_files = [p.strip() for p in args.ela_files.split(",") if p.strip()]
    discovered_ela_files = _discover_ela_files(resources_path, years)
    ela_files = explicit_ela_files or discovered_ela_files
    if not ela_files:
        ela_files = [ela_file]
    explicit_indicator_paths = [
        p.strip() for p in args.indicators_paths.split(",") if p.strip()
    ]
    indicator_paths = explicit_indicator_paths or _discover_indicator_paths(
        indicators_path=indicators_path,
        resources_path=resources_path,
        years=years,
        source=indicators_source,
    )

    if args.mode in {"full", "initial_data", "migrate_only"}:
        run_step(["-m", "alembic", "upgrade", "head"], "migrate")

    if args.mode in {"full", "initial_data"}:
        run_step(["app/scripts/initial_data.py"], "initial_data")

    if not args.skip_sync and args.mode in {
        "full",
        "import_ela_data",
        "import_indicators",
        "both_imports",
    }:
        run_step(
            [
                "app/scripts/gcp/sync_gcs_resources.py",
                "--uri",
                args.gcs_uri,
                "--dest",
                resources_path,
            ],
            "sync_gcs_resources",
        )
    elif args.skip_sync:
        print(
            "[pipeline] skipping sync_gcs_resources (--skip-sync enabled)", flush=True
        )

    if args.mode == "import_ela_data":
        chosen_ela_file = next((p for p in ela_files if Path(p).exists()), ela_file)
        cmd = [
            "app/scripts/cde/import_ela_data.py",
            chosen_ela_file,
            "--batch-size",
            str(args.batch_size),
        ]
        if args.overwrite:
            cmd.append("--overwrite")
        run_step(cmd, "import_ela_data")

    if args.mode == "import_indicators":
        sources = (
            ["state", "cde"] if indicators_source == "state" else [indicators_source]
        )
        for src in sources:
            # Filter paths based on the source being imported
            relevant_paths = [
                p for p in indicator_paths if _is_year_folder(Path(p).name, "", src)
            ]
            for index, indicator_path in enumerate(relevant_paths, start=1):
                cmd = [
                    "app/scripts/cde/import_indicators.py",
                    "--source",
                    src,
                    "--path",
                    indicator_path,
                    "--batch-size",
                    str(args.batch_size),
                ]
                if args.overwrite:
                    cmd.append("--overwrite")
                if args.indicator:
                    cmd.extend(["--indicator", args.indicator])
                if years:
                    cmd.extend(["--years", ",".join(years)])
                run_step(cmd, f"import_indicators_{src}_{index}")

    if args.mode in {"both_imports", "full"}:
        existing_ela_files = [p for p in ela_files if Path(p).exists()]
        if not existing_ela_files:
            raise FileNotFoundError(
                f"No ELA files found for years={years} under resources_path={resources_path}. "
                f"Tried: {ela_files}"
            )
        for index, current_ela_file in enumerate(existing_ela_files, start=1):
            cmd = [
                "app/scripts/cde/import_ela_data.py",
                current_ela_file,
                "--batch-size",
                str(args.batch_size),
            ]
            if args.overwrite:
                cmd.append("--overwrite")
            run_step(cmd, f"import_ela_data_{index}")

        sources = (
            ["state", "cde"] if indicators_source == "state" else [indicators_source]
        )
        for src in sources:
            # Filter paths based on the source being imported
            relevant_paths = [
                p for p in indicator_paths if _is_year_folder(Path(p).name, "", src)
            ]
            for index, indicator_path in enumerate(relevant_paths, start=1):
                cmd = [
                    "app/scripts/cde/import_indicators.py",
                    "--source",
                    src,
                    "--path",
                    indicator_path,
                    "--batch-size",
                    str(args.batch_size),
                    "--all-files",
                ]
                if args.overwrite:
                    cmd.append("--overwrite")
                if args.indicator:
                    cmd.extend(["--indicator", args.indicator])
                if years:
                    cmd.extend(["--years", ",".join(years)])
                run_step(cmd, f"import_indicators_all_files_{src}_{index}")

    print("[pipeline] completed", flush=True)


if __name__ == "__main__":
    main()
