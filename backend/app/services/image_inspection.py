import hashlib
import io
from PIL import Image, UnidentifiedImageError


def inspect_image(content: bytes) -> dict:
    """Return basic, non-verdict image facts.

    Metadata presence or absence does not establish whether an image is authentic.
    """
    if not content:
        raise ValueError("The uploaded file is empty.")

    try:
        with Image.open(io.BytesIO(content)) as image:
            image.verify()

        with Image.open(io.BytesIO(content)) as image:
            exif = image.getexif()
            exif_tags = sorted(str(tag_id) for tag_id in exif.keys())
            return {
                "sha256": hashlib.sha256(content).hexdigest(),
                "format": image.format,
                "width": image.width,
                "height": image.height,
                "mode": image.mode,
                "metadata": {
                    "exif_present": bool(exif_tags),
                    "exif_tag_ids": exif_tags,
                    "provenance_status": "not_assessed",
                },
                "assessment": {
                    "status": "insufficient_evidence",
                    "message": (
                        "This first version reports file properties only. "
                        "It does not determine whether the image is real, "
                        "AI-generated, or manipulated."
                    ),
                },
            }
    except (UnidentifiedImageError, OSError, SyntaxError) as exc:
        raise ValueError("The file could not be decoded as a supported image.") from exc
