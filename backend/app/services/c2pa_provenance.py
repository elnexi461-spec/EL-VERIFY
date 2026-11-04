"""C2PA Content Credentials inspection.

This module verifies embedded provenance with the official C2PA Python SDK.
Remote manifest and OCSP fetching are disabled so uploaded files cannot cause
arbitrary outbound requests from the server.
"""
import json
import os
import tempfile

FORMAT_EXTENSIONS = {"JPEG": ".jpg", "PNG": ".png", "WEBP": ".webp", "TIFF": ".tiff"}


def _validation_items(reader):
    try:
        findings = reader.get_validation_results()
    except Exception:
        return []
    if not isinstance(findings, (list, tuple)):
        return []
    safe_findings = []
    for item in findings[:50]:
        if not isinstance(item, dict):
            safe_findings.append({"detail": str(item)[:500]})
            continue
        safe = {}
        for key in ("code", "explanation", "success", "severity"):
            value = item.get(key)
            if isinstance(value, (str, bool, int, float)):
                safe[key] = value[:500] if isinstance(value, str) else value
        if safe:
            safe_findings.append(safe)
    return safe_findings


def _manifest_summary(store):
    if not isinstance(store, dict):
        return {"available": False}
    active_label = store.get("active_manifest")
    manifests = store.get("manifests")
    if not isinstance(active_label, str) or not isinstance(manifests, dict):
        return {"available": False}
    active = manifests.get(active_label)
    if not isinstance(active, dict):
        return {"available": False}

    signature = active.get("signature_info")
    if not isinstance(signature, dict):
        signature = {}
    assertions = active.get("assertions")
    ingredients = active.get("ingredients")
    if not isinstance(assertions, list):
        assertions = []
    if not isinstance(ingredients, list):
        ingredients = []

    claim_generator = active.get("claim_generator")
    if not isinstance(claim_generator, str) or not claim_generator.strip():
        generator_info = active.get("claim_generator_info")
        if isinstance(generator_info, list):
            names = [
                str(item.get("name", "")).strip()
                for item in generator_info
                if isinstance(item, dict) and item.get("name")
            ]
            claim_generator = ", ".join(names)
        else:
            claim_generator = ""

    return {
        "available": True,
        "title": str(active.get("title", ""))[:300] or None,
        "claim_generator": str(claim_generator)[:300] or None,
        "signature_info": {
            key: str(signature[key])[:300]
            for key in ("alg", "issuer", "time")
            if signature.get(key) is not None
        },
        "assertion_labels": [
            str(item.get("label", ""))[:200]
            for item in assertions[:100]
            if isinstance(item, dict) and item.get("label") is not None
        ],
        "ingredient_count": len(ingredients),
    }


def inspect_c2pa_provenance(content: bytes, image_format: str) -> dict:
    """Inspect C2PA provenance without retaining uploads or making network calls."""
    extension = FORMAT_EXTENSIONS.get(image_format)
    if not extension:
        return {"status": "unsupported_format", "message": "C2PA inspection is not enabled for this format."}
    try:
        import c2pa
    except ImportError:
        return {"status": "unavailable", "message": "The C2PA verification library is not installed."}

    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=extension, delete=False) as temp_file:
            temp_file.write(content)
            temp_path = temp_file.name

        context = c2pa.Context.from_dict({
            "verify": {"remote_manifest_fetch": False, "ocsp_fetch": False}
        })
        with context:
            with c2pa.Reader(temp_path, context=context) as reader:
                store = json.loads(reader.json())
                try:
                    validation_state = str(reader.get_validation_state())
                except Exception:
                    validation_state = "not_reported"
                return {
                    "status": "found",
                    "manifest_location": "embedded" if reader.is_embedded() else "external_reference",
                    "validation_state": validation_state[:200],
                    "validation_results": _validation_items(reader),
                    "manifest": _manifest_summary(store),
                    "interpretation": (
                        "A C2PA manifest records signed provenance claims. Validation describes "
                        "the manifest and its signature; it does not prove every claim is true "
                        "or that the depicted event happened."
                    ),
                }
    except Exception as exc:
        error_text = str(exc)
        lowered = error_text.lower()
        if "manifestnotfound" in lowered or "no jumbf data found" in lowered:
            return {
                "status": "absent",
                "message": "No embedded C2PA Content Credentials were found.",
                "interpretation": (
                    "Absence of Content Credentials does not mean an image is fake, "
                    "AI-generated, or manipulated."
                ),
            }
        return {
            "status": "unable_to_read",
            "message": "The C2PA manifest could not be read or validated.",
            "detail": error_text[:500],
        }
    finally:
        if temp_path:
            try:
                os.unlink(temp_path)
            except OSError:
                pass
