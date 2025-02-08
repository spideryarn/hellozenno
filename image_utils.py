from PIL import Image
from io import BytesIO
from pathlib import Path
from typing import Union


def get_image_size(image_data: bytes) -> int:
    """Get size of image data in bytes."""
    return len(image_data)


def resize_image_to_target_size(
    image_data: Union[bytes, Path, str],
    max_size: int,
    *,
    initial_scale_factor: float = 0.95,
    min_scale_factor: float = 0.1,
) -> tuple[bytes, dict]:
    """Resize image while maintaining aspect ratio until it's under max_size.

    Args:
        image_data: Image data as bytes or path to image file
        max_size: Maximum size in bytes
        initial_scale_factor: Initial scale factor to try (0.95 = reduce to 95%)
        min_scale_factor: Minimum scale factor to try before giving up

    Returns:
        Tuple of (resized_image_data, metadata) where metadata contains:
            - original_size: Size of original image in bytes
            - final_size: Size of resized image in bytes
            - scale_factor: Final scale factor used

    Raises:
        ValueError: If image cannot be resized to target size
        IOError: If image format is not supported
    """
    # If image_data is a path, read it
    if isinstance(image_data, (str, Path)):
        with open(image_data, "rb") as f:
            image_data = f.read()

    # Get original size
    original_size = len(image_data)

    # If already under max size, return as-is
    if original_size <= max_size:
        return image_data, {
            "original_size": original_size,
            "final_size": original_size,
            "was_resized": False,
        }

    # Open image
    img = Image.open(BytesIO(image_data))

    # Get original format
    format = img.format or "JPEG"

    # Get original dimensions
    width, height = img.size

    # Try progressively smaller scale factors
    scale_factor = initial_scale_factor
    while scale_factor >= min_scale_factor:
        # Calculate new dimensions
        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)

        # Resize image
        resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Save to bytes
        output = BytesIO()
        resized.save(output, format=format)
        resized_data = output.getvalue()

        # Check if small enough
        if len(resized_data) <= max_size:
            return resized_data, {
                "original_size": original_size,
                "final_size": len(resized_data),
                "was_resized": True,
                "scale_factor": scale_factor,
            }

        # Try smaller scale factor
        scale_factor *= 0.9

    raise ValueError(
        f"Could not resize image to under {max_size} bytes "
        f"(minimum scale factor: {min_scale_factor})"
    )
