from google.cloud import storage
import os
import json
from pathlib import Path
from typing import List
import fnmatch
from urllib.parse import quote

from gdutils.strings import PathOrStr
from obsolete.google_cloud_run_utils import get_credentials


def get_storage_client() -> storage.Client:
    """Get a Google Cloud Storage client.

    Uses application default credentials:
    - Local: reads GOOGLE_APPLICATION_CREDENTIALS environment variable
    - Cloud Run: automatically uses the service account
    """
    # No need to check credentials on Cloud Run
    credentials_path = get_credentials()
    if credentials_path is not None and not os.path.exists(credentials_path):
        raise ValueError(f"Credentials file not found at {credentials_path}")
    return storage.Client()


def list_blobs(
    bucket_name: str,
    prefix: PathOrStr = "",
    pattern: str = "*",
    verbose: int = 0,
) -> List[str]:
    """List blobs in a bucket, optionally filtered by prefix and glob pattern.

    Args:
        bucket_name: Name of the GCS bucket
        prefix: Optional prefix to filter blobs (like a directory)
        pattern: Optional glob pattern to filter blob names (e.g. "*.json")
        verbose: Verbosity level

    Returns:
        List of blob names (paths relative to bucket root)
    """
    prefix = str(prefix) if prefix else ""
    client = get_storage_client()
    bucket = client.bucket(bucket_name)
    blobs = list(bucket.list_blobs(prefix=prefix))

    # Filter by pattern if provided
    if pattern != "*":
        blob_names = [
            blob.name
            for blob in blobs
            if fnmatch.fnmatch(os.path.basename(blob.name), pattern)
        ]
    else:
        blob_names = [blob.name for blob in blobs]

    if verbose:
        print(
            f"Found {len(blob_names)} blobs matching pattern '{pattern}' with prefix '{prefix}'"
        )
    return blob_names


def upload_file(
    bucket_name: str,
    source_file: PathOrStr,
    destination_blob: PathOrStr,
    verbose: int = 0,
) -> None:
    """Upload a file to GCS.

    Args:
        bucket_name: Name of the GCS bucket
        source_file: Local file path to upload
        destination_blob: Destination path in GCS
        verbose: Verbosity level
    """
    client = get_storage_client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(str(destination_blob))
    blob.upload_from_filename(str(source_file))
    if verbose:
        print(f"Successfully uploaded {source_file} to {destination_blob}")


def parse_gcs_uri(uri: str) -> tuple[str, str]:
    """Parse a Google Cloud Storage URI into bucket name and blob path.

    Args:
        uri: GCS URI in the format 'gs://bucket-name/path/to/blob'

    Returns:
        Tuple of (bucket_name, blob_path)
    """
    if uri.startswith("gs://"):
        # Remove gs:// prefix
        path = uri[5:]
        # Split into bucket and blob path
        bucket_name, *rest = path.split("/", 1)
        blob_path = rest[0] if rest else ""
        return bucket_name, blob_path
    return "", uri


def download_file(
    bucket_name: str,
    source_blob: PathOrStr,
    destination_file: PathOrStr,
    verbose: int = 0,
) -> None:
    """Download a file from GCS.

    Args:
        bucket_name: Name of the GCS bucket
        source_blob: Source path in GCS
        destination_file: Local file path to save to
        verbose: Verbosity level
    """
    client = get_storage_client()
    bucket = client.bucket(bucket_name)
    # Handle potential gs:// URI format
    _, blob_path = parse_gcs_uri(str(source_blob))
    blob = bucket.blob(blob_path)
    blob.download_to_filename(str(destination_file))
    if verbose:
        print(f"Successfully downloaded {source_blob} to {destination_file}")


def write_content(
    bucket_name: str,
    destination_blob: PathOrStr,
    content: str,
    verbose: int = 0,
) -> None:
    """Write content directly to a GCS blob.

    Args:
        bucket_name: Name of the GCS bucket
        destination_blob: Destination path in GCS
        content: String content to write
        verbose: Verbosity level
    """
    client = get_storage_client()
    bucket = client.bucket(bucket_name)
    # Handle potential gs:// URI format
    _, blob_path = parse_gcs_uri(str(destination_blob))
    blob = bucket.blob(blob_path)
    blob.upload_from_string(content)
    if verbose:
        print(f"Successfully wrote content to {destination_blob}")


def read_content(
    bucket_name: str,
    source_blob: PathOrStr,
    verbose: int = 0,
) -> str:
    """Read content directly from a GCS blob.

    Args:
        bucket_name: Name of the GCS bucket
        source_blob: Source path in GCS
        verbose: Verbosity level
    """
    client = get_storage_client()
    bucket = client.bucket(bucket_name)
    # Handle potential gs:// URI format
    _, blob_path = parse_gcs_uri(str(source_blob))
    if verbose:
        print(f"Attempting to read from blob: {blob_path}")
    blob = bucket.blob(blob_path)
    content = blob.download_as_text()
    if verbose:
        print(f"Successfully read content from {blob_path}")
    return content


def write_json(
    bucket_name: str,
    destination_blob: PathOrStr,
    data: dict,
    indent: int = 2,
    sort_keys: bool = False,
    ensure_ascii: bool = True,
    verbose: int = 0,
) -> None:
    """Write JSON data directly to a GCS blob.

    Args:
        bucket_name: Name of the GCS bucket
        destination_blob: Destination path in GCS
        data: Dictionary to serialize and write
        indent: Number of spaces for indentation
        sort_keys: Whether to sort dictionary keys
        ensure_ascii: Whether to escape non-ASCII characters
        verbose: Verbosity level
    """
    content = json.dumps(
        data, indent=indent, sort_keys=sort_keys, ensure_ascii=ensure_ascii
    )
    write_content(bucket_name, str(destination_blob), content, verbose)


def read_json(
    bucket_name: str,
    source_blob: PathOrStr,
    verbose: int = 0,
) -> dict:
    """Read JSON data directly from a GCS blob.

    Args:
        bucket_name: Name of the GCS bucket
        source_blob: Source path in GCS
        verbose: Verbosity level
    """
    content = read_content(bucket_name, str(source_blob), verbose)
    return json.loads(content)
