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


def test_real_signed_image_manifest_is_read_and_signature_is_reported(tmp_path, monkeypatch):
    """Sign an image with a disposable CA/leaf chain and inspect its manifest."""
    import datetime
    import io

    from cryptography import x509
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import ec
    from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID
    from PIL import Image
    import c2pa

    now = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
    root_key = ec.generate_private_key(ec.SECP256R1())
    root_name = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, "EL-VERIFY disposable test root"),
    ])
    root_certificate = (
        x509.CertificateBuilder()
        .subject_name(root_name)
        .issuer_name(root_name)
        .public_key(root_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - datetime.timedelta(minutes=1))
        .not_valid_after(now + datetime.timedelta(days=2))
        .add_extension(x509.BasicConstraints(ca=True, path_length=0), critical=True)
        .add_extension(
            x509.KeyUsage(
                digital_signature=True,
                content_commitment=False,
                key_encipherment=False,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=True,
                crl_sign=True,
                encipher_only=None,
                decipher_only=None,
            ),
            critical=True,
        )
        .add_extension(x509.SubjectKeyIdentifier.from_public_key(root_key.public_key()), critical=False)
        .sign(root_key, hashes.SHA256())
    )
    leaf_key = ec.generate_private_key(ec.SECP256R1())
    leaf_name = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, "EL-VERIFY automated test signer"),
    ])
    leaf_certificate = (
        x509.CertificateBuilder()
        .subject_name(leaf_name)
        .issuer_name(root_name)
        .public_key(leaf_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - datetime.timedelta(minutes=1))
        .not_valid_after(now + datetime.timedelta(days=1))
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
        .add_extension(x509.SubjectKeyIdentifier.from_public_key(leaf_key.public_key()), critical=False)
        .add_extension(
            x509.AuthorityKeyIdentifier.from_issuer_public_key(root_key.public_key()),
            critical=False,
        )
        .sign(root_key, hashes.SHA256())
    )

    root_pem = root_certificate.public_bytes(serialization.Encoding.PEM)
    # C2PA expects the signer certificate followed by its issuing certificate.
    cert_chain_pem = (
        leaf_certificate.public_bytes(serialization.Encoding.PEM) + root_pem
    )
    key_pem = leaf_key.private_bytes(
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
        sign_cert=cert_chain_pem,
        private_key=key_pem,
        ta_url=None,
    )
    signing_settings = c2pa.Settings.from_dict({
        "trust": {"user_anchors": root_pem.decode("ascii")},
        "verify": {
            "remote_manifest_fetch": False,
            "ocsp_fetch": False,
            "verify_after_sign": False,
        },
        "builder": {"thumbnail": {"enabled": False}},
    })
    with c2pa.Context(signing_settings) as signing_context:
        with c2pa.Signer.from_info(signer_info) as signer:
            with c2pa.Builder(manifest, signing_context) as builder:
                with open(signed_path, "w+b") as destination:
                    builder.sign(signer, "image/jpeg", source, destination)

    # Trust the ephemeral root only for this test's read. Production inspection
    # continues to use its configured trust store and never trusts uploaded certs.
    original_from_dict = c2pa.Context.from_dict

    def test_context(settings):
        test_settings = dict(settings)
        test_settings["trust"] = {"user_anchors": root_pem.decode("ascii")}
        return original_from_dict(test_settings)

    monkeypatch.setattr(c2pa.Context, "from_dict", staticmethod(test_context))
    result = inspect_c2pa_provenance(signed_path.read_bytes(), "JPEG")

    assert result["status"] == "found"
    assert result["manifest"]["available"] is True
    assert result["manifest"]["claim_generator"] is not None
    assert result["manifest"]["assertion_labels"]
    assert result["validation_state"] != "not_reported"
    assert isinstance(result["validation_results"], list)

    # Change bytes in the JPEG entropy-coded image data while leaving the
    # embedded APP11/JUMBF manifest untouched. This should preserve the
    # manifest but break its hard binding to the image bytes.
    signed_bytes = signed_path.read_bytes()
    sos_marker = signed_bytes.find(b"\xff\xda")
    assert sos_marker >= 0, "Signed JPEG must contain a Start Of Scan marker"
    sos_length = int.from_bytes(signed_bytes[sos_marker + 2:sos_marker + 4], "big")
    entropy_start = sos_marker + 2 + sos_length
    eoi_marker = signed_bytes.rfind(b"\xff\xd9")
    assert entropy_start < eoi_marker, "Signed JPEG must contain image scan data"

    candidate_positions = range(entropy_start + 8, eoi_marker - 1)
    mutation_position = next(
        (position for position in candidate_positions if signed_bytes[position] != 0xFF),
        None,
    )
    assert mutation_position is not None, "Could not find a safe JPEG scan byte to mutate"
    tampered_bytes = bytearray(signed_bytes)
    tampered_bytes[mutation_position] ^= 0x01
    tampered_path = tmp_path / "tampered.jpg"
    tampered_path.write_bytes(tampered_bytes)

    tampered_result = inspect_c2pa_provenance(tampered_path.read_bytes(), "JPEG")
    assert tampered_result["status"] == "found", (
        "The original C2PA manifest should remain readable after image-data tampering"
    )
    findings = tampered_result["validation_results"]
    assert any(
        item.get("success") is False
        or any(
            marker in str(item.get("code", "")).lower()
            for marker in ("mismatch", "invalid", "hash")
        )
        for item in findings
    ) or tampered_result["validation_state"].lower() not in ("valid", "trusted"), (
        "Tampering should produce a validation finding, not a clean validation result"
    )
