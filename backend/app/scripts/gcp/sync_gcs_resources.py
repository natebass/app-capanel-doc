from __future__ import annotations

import argparse
from pathlib import Path
from urllib.parse import quote

import httpx

METADATA_URL = (
    "http://metadata.google.internal/computeMetadata/v1/"
    "instance/service-accounts/default/token"
)


def parse_gs_uri(uri: str) -> tuple[str, str]:
    if not uri.startswith("gs://"):
        msg = f"Expected gs:// URI, got: {uri}"
        raise ValueError(msg)
    remainder = uri.removeprefix("gs://")
    bucket, _, prefix = remainder.partition("/")
    if not bucket:
        msg = f"Bucket is missing in URI: {uri}"
        raise ValueError(msg)
    normalized_prefix = prefix.strip("/")
    if normalized_prefix:
        normalized_prefix = f"{normalized_prefix}/"
    return bucket, normalized_prefix


def _get_token_from_adc() -> str:
    """Obtain a bearer token via Application Default Credentials (local dev)."""
    try:
        import google.auth
        import google.auth.transport.requests
    except ImportError as exc:
        msg = "google-auth is not installed. Run: pip install google-auth"
        raise RuntimeError(msg) from exc

    credentials, _ = google.auth.default(
        scopes=["https://www.googleapis.com/auth/devstorage.read_only"]
    )
    request = google.auth.transport.requests.Request()
    credentials.refresh(request)  # type: ignore[no-untyped-call]
    if not credentials.token:
        msg = "ADC did not return an access token."
        raise RuntimeError(msg)
    return str(credentials.token)


def get_access_token(client: httpx.Client) -> str:
    """Return a GCS bearer token.

    Tries the GCE metadata server first (works inside Cloud Run / GCE).
    Falls back to Application Default Credentials when running locally.
    """
    try:
        response = client.get(
            METADATA_URL,
            headers={"Metadata-Flavor": "Google"},
            timeout=3.0,
        )
        response.raise_for_status()
        payload = response.json()
        token = payload.get("access_token")
        if not token:
            msg = "Metadata server response did not include access_token."
            raise RuntimeError(msg)
        return str(token)
    except (httpx.ConnectError, httpx.TimeoutException):
        print(
            "[sync_gcs_resources] GCE metadata server unreachable; "
            "falling back to Application Default Credentials.",
            flush=True,
        )
        return _get_token_from_adc()


def list_objects(
    client: httpx.Client, token: str, bucket: str, prefix: str
) -> list[str]:
    object_names: list[str] = []
    page_token: str | None = None
    headers = {"Authorization": f"Bearer {token}"}

    while True:
        params: dict[str, str] = {"prefix": prefix, "maxResults": "1000"}
        if page_token:
            params["pageToken"] = page_token
        response = client.get(
            f"https://storage.googleapis.com/storage/v1/b/{bucket}/o",
            params=params,
            headers=headers,
            timeout=30.0,
        )
        response.raise_for_status()
        payload = response.json()
        for item in payload.get("items", []):
            name = item.get("name")
            if name and not str(name).endswith("/"):
                object_names.append(str(name))
        page_token = payload.get("nextPageToken")
        if not page_token:
            break

    return object_names


def download_objects(
    client: httpx.Client,
    token: str,
    bucket: str,
    prefix: str,
    destination: Path,
    object_names: list[str],
) -> int:
    headers = {"Authorization": f"Bearer {token}"}
    downloaded_count = 0

    for object_name in object_names:
        encoded_name = quote(object_name, safe="")
        response = client.get(
            f"https://storage.googleapis.com/storage/v1/b/{bucket}/o/{encoded_name}",
            params={"alt": "media"},
            headers=headers,
            timeout=120.0,
        )
        response.raise_for_status()

        relative_name = object_name
        if prefix and relative_name.startswith(prefix):
            relative_name = relative_name[len(prefix) :]
        if not relative_name:
            continue

        output_path = destination / relative_name
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(response.content)
        downloaded_count += 1

    return downloaded_count


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Sync objects from a gs:// bucket prefix into a local folder."
    )
    parser.add_argument(
        "--uri",
        required=True,
        help="Source GCS URI, for example gs://ca-panel-001-resources or gs://bucket/path",
    )
    parser.add_argument(
        "--dest",
        required=True,
        help="Destination directory inside the container.",
    )
    args = parser.parse_args()

    destination = Path(args.dest).resolve()
    destination.mkdir(parents=True, exist_ok=True)

    bucket, prefix = parse_gs_uri(args.uri)
    with httpx.Client(follow_redirects=True) as client:
        token = get_access_token(client)
        objects = list_objects(client, token, bucket, prefix)
        count = download_objects(client, token, bucket, prefix, destination, objects)
    print(f"Downloaded {count} object(s) from {args.uri} to {destination}")


if __name__ == "__main__":
    main()
