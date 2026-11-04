# EL-VERIFY — Architecture

## Design goal

Build a modular verification workflow that reports observable evidence and uncertainty, rather than unsupported true/false verdicts.

## Current MVP request flow

1. A user opens the browser interface served at /app/.
2. The browser sends an image to POST /api/images/inspect.
3. The API enforces the allowed MIME type and 10 MB upload limit.
4. Pillow decodes the image, verifies the file structure, enforces a pixel-count limit, and extracts basic file facts and metadata indicators.
5. The service computes a SHA-256 fingerprint.
6. The C2PA Python SDK inspects the submitted bytes using a short-lived temporary file.
7. Remote manifest fetching and OCSP fetching are disabled for this workflow.
8. The API returns a structured evidence report. Temporary files are removed after inspection.

## Current modules

- **EL-VISION:** basic image inspection and C2PA Content Credentials verification.
- **EL-TRACE:** initial file fingerprint and metadata evidence, currently implemented within EL-VISION.
- **EL-SOURCE:** planned source and claim investigation.
- **EL-IDENTITY:** planned public identity-claim investigation using corroborating evidence, not facial identification.
- **EL-INTELLIGENCE:** planned evidence synthesis and human-readable reports.

## API contract

- GET /api/health — service health.
- POST /api/images/inspect — image properties, metadata indicators, SHA-256 and C2PA result.

The C2PA result uses explicit statuses: found, absent, unsupported_format, unavailable, or unable_to_read. A found manifest includes the SDK validation state and selected validation findings. The application must not translate the presence of a manifest into a claim that the content itself is truthful.

## Security and privacy

- Enforce upload size, declared content type, decoded file format and pixel-count limits.
- Treat uploaded files as untrusted input.
- Disable remote C2PA manifest and OCSP fetching during file inspection.
- Use temporary files only where required by the SDK and delete them after inspection.
- Do not retain submitted media by default.
- Do not fetch arbitrary user-supplied URLs without SSRF protections.
- Keep secrets in environment variables.
- Log operational events without storing sensitive content.

## Planned architecture

- Add a source verification module with strict URL allowlisting and DNS/IP checks before any backend fetch.
- Evaluate synthetic-media models against public, licensed datasets before exposing scores.
- Add report export and optional user-controlled history only after a privacy review.
- Introduce background jobs only when measured analysis workloads require them.
