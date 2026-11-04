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


def test_official_sdk_reads_unsigned_jpeg_without_remote_fetches(tmp_path):
    from PIL import Image

    image_path = tmp_path / "plain.jpg"
    Image.new("RGB", (8, 8), "white").save(image_path, format="JPEG")
    result = inspect_c2pa_provenance(image_path.read_bytes(), "JPEG")

    assert result["status"] == "absent"
    assert "does not mean" in result["interpretation"]


def test_real_signed_image_manifest_is_read_and_signature_is_reported(tmp_path):
    """Create a disposable self-signed C2PA asset and inspect it with the real SDK.

    The test certificate is intentionally self-signed. It exercises manifest
    creation and cryptographic signature processing, not public signer trust.
    """
    import datetime
    import io

    from cryptography import x509
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import ec
    from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID
    from PIL import Image
    import c2pa

    private_key = ec.generate_private_key(ec.SECP256R1())
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, "EL-VERIFY automated test signer"),
    ])
    now = datetime.datetime.now(datetime.timezone.utc)
    certificate = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(private_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before((now - datetime.timedelta(minutes=1)).replace(tzinfo=None))
        .not_valid_after((now + datetime.timedelta(days=1)).replace(tzinfo=None))
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .add_extension(
            x509.KeyUsage(
                digital_signature=True,
                content_commitment=False,
                key_encipherment=False,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=False,
                crl_sign=False,
                encipher_only=None,
                decipher_only=None,
            ),
            critical=True,
        )
        .add_extension(
            x509.ExtendedKeyUsage([ExtendedKeyUsageOID.EMAIL_PROTECTION]),
            critical=False,
        )
        .sign(private_key, hashes.SHA256())
    )
    cert_pem = certificate.public_bytes(serialization.Encoding.PEM)
    key_pem = private_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )

    source = io.BytesIO()
    Image.new("RGB", (24, 16), "white").save(source, format="JPEG")
    source.seek(0)
    signed_path = tmp_path / "signed.jpg"
    manifest = {
        "claim_generator_info": [{"name": "EL-VERIFY-test", "version": "0.1"}],
        "format": "image/jpeg",
        "title": "EL-VERIFY disposable signed test image",
        "assertions": [{
            "label": "c2pa.actions",
            "data": {"actions": [{
                "action": "c2pa.created",
                "digitalSourceType": "http://cv.iptc.org/newscodes/digitalsourcetype/digitalCreation",
            }]},
        }],
    }

    signer_info = c2pa.C2paSignerInfo(
        alg=c2pa.C2paSigningAlg.ES256,
        sign_cert=cert_pem,
        private_key=key_pem,
        ta_url=None,
    )
    settings = c2pa.Settings.from_dict({
        "verify": {"remote_manifest_fetch": False, "ocsp_fetch": False},
        "builder": {"thumbnail": {"enabled": False}},
    })
    with c2pa.Context(settings) as signing_context:
        with c2pa.Signer.from_info(signer_info) as signer:
            with c2pa.Builder(manifest, signing_context) as builder:
                with open(signed_path, "w+b") as destination:
                    builder.sign(signer, "image/jpeg", source, destination)

    result = inspect_c2pa_provenance(signed_path.read_bytes(), "JPEG")

    assert result["status"] == "found"
    assert result["manifest"]["available"] is True
    assert result["manifest"]["claim_generator"] is not None
    assert result["manifest"]["assertion_labels"]
    assert result["validation_state"] != "not_reported"
    assert isinstance(result["validation_results"], list)
    # The SDK must return its validation state and findings. The self-signed
    # certificate is deliberately not treated as a trusted signer.
