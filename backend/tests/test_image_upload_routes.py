import io

from fastapi.testclient import TestClient
from PIL import Image

from app.main import app

client = TestClient(app)


def make_png():
    image = Image.new("RGB", (2, 2), "white")
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def test_pdf_upload_is_rejected_as_unsupported_type():
    response = client.post(
        "/api/images/inspect",
        files={"file": ("document.pdf", b"%PDF-1.4 test", "application/pdf")},
    )

    assert response.status_code == 415
    assert response.json()["detail"] == "Unsupported image type."


def test_upload_over_10mb_is_rejected():
    oversized_content = b"x" * (10 * 1024 * 1024 + 1)
    response = client.post(
        "/api/images/inspect",
        files={"file": ("large.png", oversized_content, "image/png")},
    )

    assert response.status_code == 413
    assert response.json()["detail"] == "Image exceeds the 10 MB limit."


def test_declared_type_must_match_actual_image_content():
    response = client.post(
        "/api/images/inspect",
        files={"file": ("mismatch.jpg", make_png(), "image/jpeg")},
    )

    assert response.status_code == 415
    assert response.json()["detail"] == (
        "The uploaded file content does not match its declared image type."
    )
