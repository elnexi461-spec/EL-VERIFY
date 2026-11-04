import hashlib
import io
import warnings

from PIL import Image, UnidentifiedImageError
from PIL.Image import DecompressionBombError, DecompressionBombWarning


MAX_IMAGE_PIXELS = 40_000_000
SUPPORTED_FORMATS = {"JPEG", "PNG", "WEBP", "TIFF"}


def inspect_image(content: bytes) -> dict:
    """Return reproducible file facts without making an authenticity verdict."""
    if not content:
        raise ValueError("The uploaded file is empty.")

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", DecompressionBombWarning)
            with Image.open(io.BytesIO(content)) as image:
                image_format = image.format
                if image_format not in SUPPORTED_FORMATS:
                    raise ValueError("The decoded image format is not supported.")
                if image.width * image.height > MAX_IMAGE_PIXELS:
                    raise ValueError("Image dimensions exceed the safety limit.")
                image.verify()

            with Image.open(io.BytesIO(content)) as image:
                exif = image.getexif()
                exif_tag_ids = sorted(str(tag_id) for tag_id in exif.keys())
                info_keys = sorted(str(key) for key in image.info.keys())
                metadata_present = bool(exif_tag_ids or info_keys)
                return {
                    "sha256": hashlib.sha256(content).hexdigest(),
                    "file_size_bytes": len(content),
                    "format": image.format,
                    "width": image.width,
                    "height": image.height,
                    "mode": image.mode,
                    "metadata": {
                        "present": metadata_present,
                        "exif_present": bool(exif_tag_ids),
                        "exif_tag_ids": exif_tag_ids,
                        "embedded_metadata_fields": info_keys,
                        "provenance_status": "not_assessed",
                        "interpretation": (
                            "Metadata can be missing, edited, or copied. "
                            "Its presence does not establish authenticity."
                        ),
                    },
                    "assessment": {
                        "status": "insufficient_evidence",
                        "message": (
                            "This version reports file properties and metadata "
                            "indicators only. It does not determine whether the "
                            "image is authentic, AI-generated, or manipulated."
                        ),
                    },
                }
    except ValueError:
        raise
    except (UnidentifiedImageError, OSError, SyntaxError, DecompressionBombError,
            DecompressionBombWarning) as exc:
        raise ValueError("The file could not be safely decoded as a supported image.") from exc
