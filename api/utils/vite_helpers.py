import os
import json
from flask import current_app, url_for
from typing import Dict, Any, Optional
from loguru import logger
import time

# Cache for manifest to avoid repeated file reads
_manifest_cache = {
    "data": None,
    "timestamp": 0,
    "ttl": 5,
}  # 5 seconds TTL in development


def get_vite_manifest() -> Dict[str, Any]:
    """
    Load the Vite manifest file from the static directory.
    Returns the manifest as a dictionary or an empty dict if not found.

    Uses caching to avoid repeated file system access with a short TTL.
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

        static_folder = current_app.static_folder
        if static_folder is None:
            current_app.logger.warning("Flask app has no static_folder configured")
            return {}

        # Try multiple manifest locations - keep it explicit for better debugging
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
        logger.warning(f"No valid Vite manifest found in any location")
        return {}
    except Exception as e:
        logger.error(f"Error loading Vite manifest: {e}")
        return {}


def vite_asset_url(asset_name: str) -> str:
    """
    Get the URL for a Vite asset using the manifest.
    Falls back to a simple path if manifest isn't available.

    Args:
        asset_name: The name of the asset (e.g., 'style.css', 'js/hz-components.es.js')

    Returns:
        The URL for the asset
    """
    manifest = get_vite_manifest()
    fallback_path = None

    # Define common fallbacks for critical assets
    common_fallbacks = {
        "style.css": "build/assets/style.css",
        "js/hz-components.es.js": "build/js/hz-components.es.js",
    }

    # Check if the asset is in the manifest
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

    # Use common fallbacks if defined
    if asset_name in common_fallbacks:
        fallback_path = common_fallbacks[asset_name]
        logger.warning(f"Using fallback path for {asset_name}: {fallback_path}")
        return url_for("static", filename=fallback_path)

    # Last resort fallback - direct path
    logger.warning(
        f"No manifest entry or fallback defined for {asset_name}, using direct path"
    )
    return url_for("static", filename=f"build/{asset_name}")


def dump_manifest():
    """
    Return a formatted string representation of the Vite manifest.
    Useful for debugging.
    """
    manifest = get_vite_manifest()
    if not manifest:
        return "No manifest data available"

    return json.dumps(manifest, indent=2)


def register_vite_helpers(app):
    """
    Register Vite helper functions with the Flask app.
    Makes them available in templates.
    """

    @app.context_processor
    def inject_vite_helpers():
        return {
            "vite_manifest": get_vite_manifest,
            "vite_asset_url": vite_asset_url,
            "dump_manifest": dump_manifest,
        }

    # Add a test route for examining the manifest when in development
    @app.route("/dev/vite-manifest")
    def view_vite_manifest():
        if app.config.get("IS_PRODUCTION", True) and not app.config.get(
            "LOCAL_CHECK_OF_PROD_FRONTEND", False
        ):
            return "This endpoint is only available in development mode", 403

        manifest = get_vite_manifest()
        common_assets = {
            "style.css": vite_asset_url("style.css"),
            "js/hz-components.es.js": vite_asset_url("js/hz-components.es.js"),
        }

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
            </style>
        </head>
        <body>
            <h1>Vite Manifest Viewer</h1>
            <p>Environment: {"Production" if app.config.get("IS_PRODUCTION") else "Development"}</p>
            <p>LOCAL_CHECK_OF_PROD_FRONTEND: {app.config.get("LOCAL_CHECK_OF_PROD_FRONTEND", False)}</p>
            
            <h2>Common Assets</h2>
            <div class="asset-list">
        """

        for name, url in common_assets.items():
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
