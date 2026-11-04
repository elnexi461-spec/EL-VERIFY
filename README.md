# EL-VERIFY

**Verify What You See. Trust What You Know.**

EL-VERIFY is an open-source digital trust and verification project. It helps people inspect digital content and review provenance information using transparent, evidence-based checks.

> **Status:** MVP in active development. The image inspection flow and C2PA integration are implemented in the repository. Automated CI results and production deployment still need confirmation. No AI-image or deepfake detection capability is claimed.

## MVP capabilities

- Browser-based image upload and evidence report.
- SHA-256 fingerprint, file size, decoded format, dimensions and image mode.
- EXIF tag identifiers and embedded metadata field names.
- C2PA Content Credentials inspection using the official C2PA Python SDK.
- Manifest summary, signer metadata, assertion labels and SDK validation findings when available.
- Explicit distinction between credentials found, absent, unsupported, unavailable and unable to read.
- Upload size, file type, pixel-count and image decoding safety checks.
- Temporary file cleanup after C2PA inspection; no report history or persistent media gallery.

## What the MVP does not do

- It does not determine whether an image is real, fake, AI-generated or manipulated.
- It does not establish that a statement inside a Content Credential is factually true.
- It does not treat missing metadata or missing credentials as evidence of fraud.
- It does not identify people in images or infer real-world identities.

## Run locally

Use Python 3.10 or newer. From the repository root:

    cd backend
    python -m venv .venv
    # Windows: .venv\\Scripts\\activate
    # macOS/Linux: source .venv/bin/activate
    pip install -r requirements.txt
    uvicorn app.main:app --reload

Open http://127.0.0.1:8000/ for the web interface or http://127.0.0.1:8000/docs for the API documentation.

## API

- GET /api/health
- POST /api/images/inspect

The inspection endpoint accepts JPEG, PNG, WEBP and TIFF uploads up to 10 MB.

C2PA remote manifest fetching and OCSP network fetching are disabled in the current service configuration. This keeps submitted media from triggering arbitrary outbound requests. Trust evaluation still depends on the SDK's configured trust anchors and validation state.

## Repository layout

- backend/ — FastAPI service and inspection modules.
- frontend/ — browser interface (HTML, CSS and JavaScript).
- docs/ — architecture, roadmap, responsible-use and contribution guidance.
- .github/workflows/ — automated backend tests.

## Responsible-use principles

- Automated model scores are indicators, not verdicts.
- Missing metadata is not proof of manipulation.
- Identity assessments must not infer who a person is from an image.
- Only analyze content the user is authorized to submit.
- Do not scrape private content or bypass platform access controls.
- Show evidence, uncertainty and limitations in every report.

## License

License selection is pending. Until a license is added, do not assume the project is licensed for reuse.
