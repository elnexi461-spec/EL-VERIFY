from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


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
    # PNG signature and payload are deliberately declared as JPEG.
    png_content = (
        b"\x89PNG\r\n\x1a\n"
        b"\x00\x00\x00\rIHDR"
        b"\x00\x00\x00\x01\x00\x00\x00\x01"
        b"\x08\x02\x00\x00\x00"
        b"\x90wS\xde"
    )
    response = client.post(
        "/api/images/inspect",
        files={"file": ("mismatch.jpg", png_content, "image/jpeg")},
    )

    assert response.status_code == 400 or response.status_code == 415
