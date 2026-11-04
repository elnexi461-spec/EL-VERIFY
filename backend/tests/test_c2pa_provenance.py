import json
import sys
from types import SimpleNamespace

from app.services.c2pa_provenance import inspect_c2pa_provenance


class FakeReader:
    def __init__(self, path, context=None):
        self.path = path

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def json(self):
        return json.dumps({
            "active_manifest": "active",
            "manifests": {
                "active": {
                    "title": "Sample photograph",
                    "claim_generator": "Camera App",
                    "signature_info": {"alg": "Es256", "issuer": "Example Signer"},
                    "assertions": [{"label": "c2pa.actions"}],
                    "ingredients": [],
                }
            },
        })

    def get_validation_state(self):
        return "Valid"

    def get_validation_results(self):
        return [{"code": "claim.signature.validated", "success": True}]

    def is_embedded(self):
        return True


class FakeContext:
    def __init__(self, settings):
        self.settings = settings

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    @classmethod
    def from_dict(cls, settings):
        return cls(settings)


def test_c2pa_manifest_summary_is_extracted(monkeypatch):
    monkeypatch.setitem(sys.modules, "c2pa", SimpleNamespace(Context=FakeContext, Reader=FakeReader))
    result = inspect_c2pa_provenance(b"fake image bytes", "JPEG")
    assert result["status"] == "found"
    assert result["manifest_location"] == "embedded"
    assert result["validation_state"] == "Valid"
    assert result["manifest"]["claim_generator"] == "Camera App"
    assert result["manifest"]["assertion_labels"] == ["c2pa.actions"]
    assert "does not prove" in result["interpretation"]


def test_no_manifest_is_absent_not_fake(monkeypatch):
    class MissingReader(FakeReader):
        def __enter__(self):
            raise RuntimeError("ManifestNotFound: no JUMBF data found")

    monkeypatch.setitem(sys.modules, "c2pa", SimpleNamespace(Context=FakeContext, Reader=MissingReader))
    result = inspect_c2pa_provenance(b"fake image bytes", "PNG")
    assert result["status"] == "absent"
    assert "does not mean" in result["interpretation"]


def test_sdk_errors_are_not_misreported_as_absence(monkeypatch):
    class BrokenReader(FakeReader):
        def __enter__(self):
            raise RuntimeError("signature validation crashed")

    monkeypatch.setitem(sys.modules, "c2pa", SimpleNamespace(Context=FakeContext, Reader=BrokenReader))
    result = inspect_c2pa_provenance(b"fake image bytes", "WEBP")
    assert result["status"] == "unable_to_read"
