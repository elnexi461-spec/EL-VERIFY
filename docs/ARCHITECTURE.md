# EL-VERIFY — Architecture (Draft)

## Design goal

Build a modular verification workflow that reports observable evidence and uncertainty, rather than unsupported true/false verdicts.

## Initial request flow

1. A user uploads an image to the API.
2. The API validates content type and size.
3. The image-inspection service decodes the file.
4. The service computes a SHA-256 fingerprint and extracts basic properties and available EXIF tag identifiers.
5. The API returns a structured report with explicit limitations.

## Planned modules

- **EL-VISION:** image/video inspection and research-backed synthetic-media indicators.
- **EL-SOURCE:** URL and claim source investigation using permitted, transparent sources.
- **EL-TRACE:** metadata and content-provenance inspection.
- **EL-IDENTITY:** investigation of public identity claims and possible impersonation using corroborating evidence, not facial identification.
- **EL-INTELLIGENCE:** combines module findings into a human-readable evidence report.

## Proposed later architecture

- Frontend: Next.js.
- API: Python / FastAPI.
- Storage: PostgreSQL for user-authorized report metadata; object storage only when necessary.
- Background jobs: introduce a queue only when analysis workloads require it.
- Model layer: evaluate open models against documented datasets before deployment.

## Security requirements

- Enforce upload size and file-type limits.
- Treat uploaded files and URLs as untrusted input.
- Do not fetch arbitrary URLs from the backend without SSRF protections.
- Avoid retaining submitted media by default.
- Keep secrets in environment variables.
- Log operational events without storing sensitive content.
