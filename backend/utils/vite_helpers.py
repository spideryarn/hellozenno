"""
Vite asset management and manifest handling utilities.

This module provides functions for loading and using the Vite manifest
file to resolve asset paths in both development and production environments.
"""

import os
import json
import time
from flask import current_app, url_for
from typing import Dict, Any, Optional, Callable
from loguru import logger

# Cache for manifest to avoid repeated file reads
_manifest_cache = {
    "data": None,
    "timestamp": 0,
    "ttl": 5,  # Default TTL in seconds
}


# Custom exceptions for clearer error messages
class ViteManifestError(Exception):
    """Raised when the Vite manifest cannot be found or is invalid."""

    pass


class ViteAssetError(Exception):
    """Raised when a requested asset cannot be found in the Vite manifest."""

    pass


def get_vite_manifest() -> Dict[str, Any]:
    """
    Load the Vite manifest file from the static directory.
    Returns the manifest as a dictionary.

    Raises:
        ViteManifestError: If manifest cannot be found or is invalid

    Returns:
        Dict[str, Any]: The manifest data
    """
    try:
        # Check if we're in development mode - shorter cache TTL if so
        is_dev = not current_app.config.get("IS_PRODUCTION", False)
        cache_ttl = 1 if is_dev else 60  # 1 second in dev, 60 seconds in prod

        # Return cached manifest if still valid
        now = time.time()
        if (
            _manifest_cache["data"] is not None
            and now - _manifest_cache["timestamp"] < cache_ttl
        ):
            return _manifest_cache["data"]

        # Get the root directory
        static_folder = current_app.static_folder
        if static_folder is None:
            raise ViteManifestError("Flask app has no static_folder configured")

        # Try multiple manifest locations
        manifest_locations = [
            os.path.join(static_folder, "build", "manifest.json"),  # Copied location
            os.path.join(
                static_folder, "build", ".vite", "manifest.json"
            ),  # Original location
        ]

        # Try each location in order
        for manifest_path in manifest_locations:
            if os.path.exists(manifest_path):
                logger.debug(f"Loading Vite manifest from {manifest_path}")

                with open(manifest_path, "r") as f:
                    manifest_data = json.load(f)

                # Quick validation - check we have at least some entries
                if not isinstance(manifest_data, dict) or len(manifest_data) == 0:
                    logger.warning(
                        f"Vite manifest at {manifest_path} is empty or invalid"
                    )
                    continue

                # Update cache
                _manifest_cache["data"] = manifest_data
                _manifest_cache["timestamp"] = now

                logger.info(
                    f"Loaded valid Vite manifest from {manifest_path} with {len(manifest_data)} entries"
                )
                return manifest_data

        # If we get here, no valid manifest was found
        raise ViteManifestError(
            f"No valid Vite manifest found in: {', '.join(manifest_locations)}"
        )
    except ViteManifestError:
        # Re-raise specific exceptions
        raise
    except Exception as e:
        # Wrap generic exceptions
        raise ViteManifestError(f"Error loading Vite manifest: {e}")


def vite_asset_url(asset_name: str) -> str:
    """
    Get the URL for a Vite asset using the manifest.

    Args:
        asset_name: The name of the asset (e.g., 'style.css', 'js/hz-components.es.js')

    Returns:
        str: The URL for the asset

    Raises:
        ViteManifestError: If the manifest cannot be loaded
        ViteAssetError: If the asset cannot be found in the manifest
    """
    # Get manifest - this will raise ViteManifestError if there's a problem
    manifest = get_vite_manifest()

    # Special case for the bundle - look for the entry point that outputs this file
    if asset_name == "js/hz-components.es.js":
        # First, check direct entry
        if asset_name in manifest and "file" in manifest[asset_name]:
            hashed_file = manifest[asset_name]["file"]
            logger.debug(
                f"Asset {asset_name} resolved to {hashed_file} via direct manifest entry"
            )
            return url_for("static", filename=f"build/{hashed_file}")

        # Next, look for entries that output to this file
        for key, value in manifest.items():
            if "file" in value and value["file"] == asset_name:
                logger.debug(f"Asset {asset_name} found via manifest entry {key}")
                return url_for("static", filename=f"build/{value['file']}")

        # Finally, check if any entry has "src/entries/index.ts" as key
        if (
            "src/entries/index.ts" in manifest
            and "file" in manifest["src/entries/index.ts"]
        ):
            bundle_file = manifest["src/entries/index.ts"]["file"]
            logger.debug(
                f"Found bundle at src/entries/index.ts which outputs to {bundle_file}"
            )
            return url_for("static", filename=f"build/{bundle_file}")

    # Check if the asset is directly in the manifest
    if asset_name in manifest and "file" in manifest[asset_name]:
        hashed_file = manifest[asset_name]["file"]
        logger.debug(f"Asset {asset_name} resolved to {hashed_file} via manifest")
        return url_for("static", filename=f"build/{hashed_file}")

    # Handle CSS files with special case
    if asset_name == "style.css":
        # Look for style.css or any style-*.css entry
        for key, value in manifest.items():
            if (
                (key.startswith("style") or "style" in key)
                and key.endswith(".css")
                and "file" in value
            ):
                logger.debug(f"Style sheet {asset_name} matched to {key} in manifest")
                return url_for("static", filename=f'build/{value["file"]}')

    # Define common critical assets for clearer error messages
    critical_assets = {
        "style.css": "build/assets/style.css",
        "js/hz-components.es.js": "build/js/hz-components.es.js",
    }

    # No entry in manifest - for critical assets, provide a clearer error message
    if asset_name in critical_assets:
        # For debugging, show what's actually in the manifest
        manifest_entries = ", ".join(manifest.keys())
        error_msg = f"Critical asset '{asset_name}' not found in Vite manifest. "
        error_msg += f"Expected at: {critical_assets[asset_name]}. "
        error_msg += f"Manifest contains: {manifest_entries}. "
        error_msg += "Check that frontend assets are built correctly."
        raise ViteAssetError(error_msg)

    # For other assets, provide a general error
    raise ViteAssetError(
        f"Asset '{asset_name}' not found in Vite manifest. "
        "Check asset name and ensure the frontend is built correctly."
    )


def dump_manifest() -> str:
    """
    Return a formatted string representation of the Vite manifest.
    Useful for debugging.

    Returns:
        str: JSON string of the manifest or an error message
    """
    manifest = get_vite_manifest()
    if not manifest:
        return "No manifest data available"

    return json.dumps(manifest, indent=2)


# ===== BACKWARD COMPATIBILITY FUNCTIONS ===== #


def load_vite_manifest() -> Dict[str, Any]:
    """
    Legacy function for backward compatibility with existing code.
    Use get_vite_manifest() for new code.

    Returns:
        Dict[str, Any]: The manifest data
    """
    logger.debug(
        "load_vite_manifest() called (legacy function) - consider migrating to get_vite_manifest()"
    )
    return get_vite_manifest()


# ===== FLASK INTEGRATION ===== #


def register_vite_helpers(app) -> None:
    """
    Register Vite helper functions with the Flask app.
    Adds a test route for examining the manifest.

    Note: This no longer registers a context processor as the
    functions are registered directly as Jinja globals in app initialization.

    Args:
        app: Flask application instance
    """

    # Add a test route for examining the manifest when in development
    @app.route("/dev/vite-manifest")
    def view_vite_manifest():
        if app.config.get("IS_PRODUCTION", True) and not app.config.get(
            "LOCAL_CHECK_OF_PROD_FRONTEND", False
        ):
            return "This endpoint is only available in development mode", 403

        # Try to load the manifest, but handle exceptions gracefully for this endpoint
        try:
            manifest = get_vite_manifest()
            manifest_error = None
        except (ViteManifestError, ViteAssetError) as e:
            manifest = {}
            manifest_error = str(e)

        # Try to get common assets, but handle exceptions
        common_assets = {}
        asset_errors = {}
        for asset_name in ["style.css", "js/hz-components.es.js"]:
            try:
                common_assets[asset_name] = vite_asset_url(asset_name)
            except Exception as e:
                asset_errors[asset_name] = str(e)

        html = f"""
        <html>
        <head>
            <title>Vite Manifest Viewer</title>
            <style>
                body {{ font-family: system-ui, -apple-system, sans-serif; line-height: 1.5; padding: 2rem; }}
                pre {{ background: #f5f5f5; padding: 1rem; overflow: auto; }}
                .asset-list {{ margin-bottom: 2rem; }}
                .asset-item {{ margin-bottom: 0.5rem; }}
                .success {{ color: green; }}
                .error {{ color: red; }}
                .warning {{ color: orange; }}
                .manifest-info {{ margin-bottom: 1.5rem; background: #f0f0f0; padding: 1rem; border-radius: 4px; }}
                .error-box {{ background: #fff5f5; border: 1px solid #fed7d7; color: #e53e3e; padding: 1rem; border-radius: 4px; margin-bottom: 1rem; }}
            </style>
        </head>
        <body>
            <h1>Vite Manifest Viewer</h1>
            
            <div class="manifest-info">
                <p><strong>Environment:</strong> {"Production" if app.config.get("IS_PRODUCTION") else "Development"}</p>
                <p><strong>LOCAL_CHECK_OF_PROD_FRONTEND:</strong> {app.config.get("LOCAL_CHECK_OF_PROD_FRONTEND", False)}</p>
                <p><strong>Cache status:</strong> {
                    "Valid (cached data)" if _manifest_cache["data"] is not None 
                    else "Empty (first request or expired)"
                }</p>
                <p><strong>Cache age:</strong> {
                    f"{time.time() - _manifest_cache['timestamp']:.2f} seconds" 
                    if _manifest_cache["data"] is not None 
                    else "N/A"
                }</p>
            </div>
            
            {f'<div class="error-box"><strong>Manifest Error:</strong> {manifest_error}</div>' if manifest_error else ''}
            
            <h2>Common Assets</h2>
            <div class="asset-list">
        """

        for name in ["style.css", "js/hz-components.es.js"]:
            if name in asset_errors:
                html += f"""
                    <div class="asset-item">
                        <strong>{name}</strong>: 
                        <span class="error">Error: {asset_errors[name]}</span>
                    </div>
                """
                continue

            url = common_assets.get(name, "")
            file_exists = False
            try:
                if url.startswith("/static/"):
                    path_part = url.split("/static/")[1]
                    if current_app.static_folder:
                        file_path = os.path.join(current_app.static_folder, path_part)
                        file_exists = os.path.exists(file_path)
            except Exception as e:
                logger.error(f"Error checking file existence: {e}")

            status_class = "success" if file_exists else "error"
            html += f"""
                <div class="asset-item">
                    <strong>{name}</strong>: 
                    <a href="{url}">{url}</a>
                    <span class="{status_class}">
                        {" ✓ File exists" if file_exists else " ✗ File NOT found"}
                    </span>
                </div>
            """

        html += f"""
            </div>
            
            <h2>Full Manifest</h2>
            <pre>{json.dumps(manifest, indent=2)}</pre>
        </body>
        </html>
        """

        return html
