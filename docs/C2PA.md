# C2PA and Content Credentials in EL-VERIFY

## What this module checks

EL-VERIFY uses the official C2PA Python SDK to look for and inspect Content Credentials attached to an uploaded image. The SDK reads the manifest store and performs the C2PA validation work. EL-VERIFY then presents a limited summary:

- Whether a manifest was found.
- Whether the manifest is embedded or referenced externally.
- The SDK's validation state and selected validation findings.
- The active manifest's title, claim generator and signature information when available.
- Assertion labels and ingredient count.

The implementation uses the SDK's Reader API. See the [official C2PA Python library](https://github.com/contentauth/c2pa-python) and its [usage guide](https://github.com/contentauth/c2pa-python/blob/main/docs/usage.md).

## How to interpret the result

C2PA is a provenance and content-history standard. It can make certain claims tamper-evident and allow validators to assess signatures, content bindings and signer credentials.

It is not a truth detector. A valid signature establishes that a particular credential signed a particular manifest and that the SDK's configured validation checks passed. It does not prove that every assertion in that manifest is true, that the signer is honest, or that the pictured event happened.

The C2PA specification explicitly separates technical validation from the consumer's broader trust decision. See the [C2PA Technical Specification](https://spec.c2pa.org/specifications/specifications/2.5/specs/C2PA_Specification.html).

## Result statuses

- `found`: the SDK returned a manifest store. Review the SDK validation state and findings; do not interpret this status alone as trusted.
- `absent`: no embedded C2PA manifest was found. This is not evidence that the image is fake or manipulated.
- `unsupported_format`: this service does not currently pass the file format to the C2PA reader.
- `unavailable`: the C2PA Python package is not installed in the runtime.
- `unable_to_read`: the SDK could not read or validate the manifest. This is not the same as a confirmed absence.

## Network and privacy controls

- The upload is written to a uniquely named temporary file because the SDK Reader accepts a file path.
- The temporary file is deleted in a `finally` block after inspection.
- Remote manifest fetching is disabled.
- OCSP fetching is disabled.
- The image itself is not persisted in an application database or gallery.
- The browser interface does not send the file to third-party font services.

The service currently relies on the SDK's default trust configuration. Production deployment should explicitly document and review trust anchors, certificate revocation policy, timestamp validation and any operational trade-offs before claiming a signer is trusted.

## Current verification coverage

Automated tests cover:
- Manifest summary formatting with a mocked SDK response.
- Distinguishing an absent manifest from an SDK error.
- A real SDK smoke test against an unsigned JPEG.
- Signing a JPEG with a disposable test CA and leaf certificate, then inspecting it through EL-VERIFY.
- Mutating the signed JPEG's entropy-coded image data while preserving its embedded C2PA manifest, then checking that the SDK validation state changes from `Valid` to `Invalid`.

The signed-image test uses a generated ES256 key pair and a temporary CA/leaf certificate chain. The test trusts that temporary root only inside the test read context. It does not add the test root to production trust settings or claim that the signer is publicly trusted. The tampering case changes image bytes without removing the manifest. It verifies that the SDK changes the overall validation state from `Valid` to `Invalid`; the current SDK response for this fixture does not include granular validation findings, so the test does not claim a specific failure code. A validation failure is a technical integrity signal, not a conclusion that the image or its creator is fake.
