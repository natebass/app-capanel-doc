from __future__ import annotations

import argparse
import json
import secrets
import string
from collections.abc import Iterable
from dataclasses import dataclass

TARGET_ALL = "all"
TARGET_GCLOUD = "gcloud"
TARGET_LOCAL_DB = "local-db"
TARGET_SECRET_KEY = "secret-key"

ALL_TARGETS = {
    TARGET_ALL,
    TARGET_GCLOUD,
    TARGET_LOCAL_DB,
    TARGET_SECRET_KEY,
}


@dataclass(frozen=True)
class RotationConfig:
    password_length: int
    output_format: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate rotated secret values for exposed credentials. "
            "Select one or more targets, or use --target all."
        )
    )
    parser.add_argument(
        "--target",
        action="append",
        choices=sorted(ALL_TARGETS),
        help=(
            "Secret groups to rotate. Repeat for multiple groups. "
            "Choices: all, gcloud, local-db, secret-key"
        ),
    )
    parser.add_argument(
        "--password-length",
        type=int,
        default=32,
        help="Length for generated passwords (default: 32, min: 16).",
    )
    parser.add_argument(
        "--format",
        choices=("env", "json"),
        default="env",
        help="Output format (default: env).",
    )
    return parser.parse_args()


def expand_targets(raw_targets: list[str] | None) -> set[str]:
    if not raw_targets:
        msg = (
            "No targets selected. Use --target all or pass one/more targets, "
            "for example: --target gcloud --target secret-key"
        )
        raise ValueError(msg)

    targets = set(raw_targets)
    if TARGET_ALL in targets:
        return {TARGET_GCLOUD, TARGET_LOCAL_DB, TARGET_SECRET_KEY}
    return targets


def generate_strong_password(length: int) -> str:
    if length < 16:
        msg = "--password-length must be >= 16."
        raise ValueError(msg)

    upper = string.ascii_uppercase
    lower = string.ascii_lowercase
    digits = string.digits
    punctuation = "!@#$%^&*()-_=+[]{}:,.?"
    full_alphabet = upper + lower + digits + punctuation

    required_chars = [
        secrets.choice(upper),
        secrets.choice(lower),
        secrets.choice(digits),
        secrets.choice(punctuation),
    ]
    remaining = [secrets.choice(full_alphabet) for _ in range(length - 4)]
    all_chars = required_chars + remaining
    secrets.SystemRandom().shuffle(all_chars)
    return "".join(all_chars)


def build_rotations(targets: Iterable[str], config: RotationConfig) -> dict[str, str]:
    selected = set(targets)
    values: dict[str, str] = {}

    if TARGET_SECRET_KEY in selected:
        values["SECRET_KEY"] = secrets.token_urlsafe(32)

    if TARGET_GCLOUD in selected:
        values["CLOUD_SQL_PASSWORD"] = generate_strong_password(config.password_length)

    if TARGET_LOCAL_DB in selected:
        values["POSTGRES_PASSWORD"] = generate_strong_password(config.password_length)
        values["FIRST_SUPERUSER_PASSWORD"] = generate_strong_password(
            config.password_length
        )

    return values


def print_env(values: dict[str, str]) -> None:
    for key, value in values.items():
        print(f"{key}={value}")


def main() -> int:
    """
    # Only SECRET_KEY (uses secrets.token_urlsafe(32))
    python3 backend/app/scripts/gcp/rotate_exposed_secrets.py --target secret-key

    # Only GCP-related passwords
    python3 backend/app/scripts/gcp/rotate_exposed_secrets.py --target gcloud

    # Only local DB passwords
    python3 backend/app/scripts/gcp/rotate_exposed_secrets.py --target local-db

    # Everything exposed
    python3 backend/app/scripts/gcp/rotate_exposed_secrets.py --target all

    # Combined, JSON output
    python3 backend/app/scripts/gcp/rotate_exposed_secrets.py --target gcloud --target local-db --target secret-key --format json
    """
    args = parse_args()
    try:
        config = RotationConfig(
            password_length=args.password_length,
            output_format=args.format,
        )
        selected_targets = expand_targets(args.target)
        rotated = build_rotations(selected_targets, config)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc

    if config.output_format == "json":
        print(json.dumps(rotated, indent=2))
        return 0

    print_env(rotated)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
