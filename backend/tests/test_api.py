import io

from fastapi.testclient import TestClient
from PIL import Image

from app.main import app
from app.routes import images as image_routes


def png_bytes():
    image = Image.new("RGB", (16, 10), "white")
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def test_home_serves_web_app():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert "EL-VERIFY" in response.text


def test_image_inspection_api_includes_provenance(monkeypatch):
    monkeypatch.setattr(
        image_routes,
        "inspect_c2pa_provenance",
        lambda content, image_format: {"status": "absent"},
    )
    client = TestClient(app)
    response = client.post(
        "/api/images/inspect",
        files={"file": ("sample.png", png_bytes(), "image/png")},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["format"] == "PNG"
    assert payload["provenance"]["status"] == "absent"


def test_image_content_type_must_match_actual_file():
    client = TestClient(app)
    response = client.post(
        "/api/images/inspect",
        files={"file": ("sample.png", png_bytes(), "image/jpeg")},
    )
    assert response.status_code == 415


def test_unsupported_mime_type_is_rejected_by_api():
    client = TestClient(app)
    response = client.post(
        "/api/images/inspect",
        files={"file": ("document.pdf", b"%PDF-1.7 test", "application/pdf")},
    )
    assert response.status_code == 415
    assert response.json()["detail"] == "Unsupported image type."


def test_upload_over_10_mb_is_rejected_before_image_decoding():
    client = TestClient(app)
    oversized_content = b"0" * (image_routes.MAX_UPLOAD_BYTES + 1)
    response = client.post(
        "/api/images/inspect",
        files={"file": ("oversized.png", oversized_content, "image/png")},
    )
    assert response.status_code == 413
    assert response.json()["detail"] == "Image exceeds the 10 MB limit."
