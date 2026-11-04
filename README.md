# EL-VERIFY

**Verify What You See. Trust What You Know.**

EL-VERIFY is an open-source digital trust and verification project. Its goal is to help people investigate digital content and identity claims using transparent, evidence-based checks.

> **Status:** Early development. This repository is a starting point; no detection capability is claimed to be production-ready.

## Initial MVP

The first milestone focuses on safe, explainable image inspection:
- Calculate a SHA-256 fingerprint for an uploaded image.
- Read basic image properties and available EXIF metadata.
- Report whether provenance metadata is present, absent, or unreadable.
- Return findings without claiming metadata proves authenticity.
- Establish an API foundation for future source and identity investigations.

AI-image detection, deepfake detection, social-platform integrations, and identity-risk assessment are future research areas. They require evaluation datasets, careful calibration, and transparent limitations before being presented as reliable features.

## Repository layout

- `backend/` — FastAPI service and image-inspection module.
- `docs/` — architecture, roadmap, and responsible-use principles.
- `frontend/` — reserved for the web application.
- `tests/` — automated backend tests.

## Run locally

```bash
cd backend
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs for interactive API documentation.

## Responsible-use principles

- Missing metadata is not proof of manipulation.
- Automated model scores are indicators, not verdicts.
- Identity assessments must not infer who a person is from an image.
- Only analyze content the user is authorized to submit.
- Do not scrape private content or bypass platform access controls.
- Show evidence, uncertainty, and limitations in every report.

## License

License selection is pending. Until a license is added, do not assume the project is licensed for reuse.
