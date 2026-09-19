"""Upload validation helpers.

Never trust client-supplied filenames or extensions alone — the actual
image bytes are decoded and checked before anything downstream runs.
"""
from __future__ import annotations

import uuid
from pathlib import Path

import numpy as np
from PIL import Image
import io

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}
MIN_DIMENSION = 64
MAX_DIMENSION = 8000


class ValidationError(Exception):
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(message)


def safe_filename(original_name: str) -> str:
    """Generate a collision-free, path-traversal-safe filename."""
    ext = Path(original_name or "").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        ext = ".jpg"
    return f"{uuid.uuid4().hex}{ext}"


def validate_upload(
    raw_bytes: bytes,
    filename: str,
    content_type: str | None,
    max_bytes: int,
) -> Image.Image:
    """Validate an uploaded image and return a decoded PIL image.

    Raises ValidationError with a user-safe message on any problem.
    """
    if not raw_bytes:
        raise ValidationError("EMPTY_FILE", "The uploaded file is empty.")

    if len(raw_bytes) > max_bytes:
        raise ValidationError(
            "FILE_TOO_LARGE",
            f"Image exceeds the maximum allowed size of {max_bytes // (1024 * 1024)} MB.",
        )

    ext = Path(filename or "").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValidationError(
            "UNSUPPORTED_FORMAT",
            "Unsupported file format. Please upload a JPG, PNG, or WEBP image.",
        )

    if content_type and content_type not in ALLOWED_MIME_TYPES:
        raise ValidationError(
            "UNSUPPORTED_FORMAT",
            "Unsupported file format. Please upload a JPG, PNG, or WEBP image.",
        )

    try:
        image = Image.open(io.BytesIO(raw_bytes))
        image.load()
    except Exception:
        raise ValidationError("CORRUPT_IMAGE", "This image file appears to be corrupted or unreadable.")

    if image.mode not in ("RGB", "RGBA", "L"):
        image = image.convert("RGB")
    if image.mode != "RGB":
        image = image.convert("RGB")

    w, h = image.size
    if w < MIN_DIMENSION or h < MIN_DIMENSION:
        raise ValidationError(
            "IMAGE_TOO_SMALL",
            f"Image is too small ({w}x{h}). Minimum size is {MIN_DIMENSION}x{MIN_DIMENSION}px.",
        )
    if w > MAX_DIMENSION or h > MAX_DIMENSION:
        raise ValidationError(
            "IMAGE_TOO_LARGE",
            f"Image dimensions ({w}x{h}) exceed the maximum of {MAX_DIMENSION}x{MAX_DIMENSION}px.",
        )

    return image
