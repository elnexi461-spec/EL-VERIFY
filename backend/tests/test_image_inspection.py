import io

import pytest
from PIL import Image

from app.services.image_inspection import inspect_image


def make_image(image_format="PNG", size=(12, 8)):
    image = Image.new("RGB", size, "white")
    buffer = io.BytesIO()
    image.save(buffer, format=image_format)
    return buffer.getvalue()


def test_inspection_returns_hash_dimensions_and_cautious_assessment():
    content = make_image()
    result = inspect_image(content)
    assert len(result["sha256"]) == 64
    assert result["format"] == "PNG"
    assert result["width"] == 12
    assert result["height"] == 8
    assert result["file_size_bytes"] == len(content)
    assert result["assessment"]["status"] == "insufficient_evidence"
    assert result["metadata"]["provenance_status"] == "not_assessed"


def test_empty_file_is_rejected():
    with pytest.raises(ValueError, match="empty"):
        inspect_image(b"")


def test_non_image_is_rejected():
    with pytest.raises(ValueError, match="safely decoded"):
        inspect_image(b"this is not an image")


def test_unsupported_decoded_format_is_rejected():
    content = make_image("BMP")
    with pytest.raises(ValueError, match="format is not supported"):
        inspect_image(content)


def test_excessive_dimensions_are_rejected_before_decode():
    content = make_image(size=(6500, 6500))
    with pytest.raises(ValueError, match="safety limit"):
        inspect_image(content)
