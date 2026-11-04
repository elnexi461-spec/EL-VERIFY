import io
from PIL import Image
from app.services.image_inspection import inspect_image


def make_png():
    image = Image.new("RGB", (12, 8), "white")
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def test_inspection_returns_hash_and_dimensions():
    result = inspect_image(make_png())
    assert len(result["sha256"]) == 64
    assert result["format"] == "PNG"
    assert result["width"] == 12
    assert result["height"] == 8
    assert result["assessment"]["status"] == "insufficient_evidence"


def test_empty_file_is_rejected():
    try:
        inspect_image(b"")
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "empty" in str(exc).lower()
