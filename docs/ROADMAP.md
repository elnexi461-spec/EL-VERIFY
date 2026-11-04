# EL-VERIFY Roadmap

## Milestone 0 — Foundation
- [x] Establish project scope and responsible-use principles.
- [x] Create FastAPI service and browser interface.
- [x] Add basic image metadata and hash inspection.
- [x] Add upload validation and image pixel-count limits.
- [x] Add API, service and C2PA test coverage.
- [ ] Confirm CI passes on GitHub Actions.
- [ ] Choose and add an open-source license.

## Milestone 1 — Image evidence and provenance
- [x] Return file size, dimensions, format, SHA-256 and metadata indicators.
- [x] Integrate official C2PA Python SDK for Content Credentials inspection.
- [x] Disable remote manifest and OCSP fetching in the upload workflow.
- [x] Return selected manifest and SDK validation details.
- [x] Build browser-based image upload and evidence report.
- [ ] Verify C2PA behaviour against real signed and unsigned fixture images.
- [ ] Add safe report export.
- [ ] Review trust-anchor configuration and validation UX.

## Milestone 2 — Source verification
- [ ] Build safe URL parsing and domain information checks.
- [ ] Add source citation and evidence capture.
- [ ] Add protections against private-network, localhost, DNS rebinding and redirect-based SSRF.
- [ ] Avoid crawling or scraping private content and respect platform terms.

## Milestone 3 — Synthetic media research
- [ ] Select public, licensed evaluation datasets.
- [ ] Benchmark candidate models for false positives and false negatives.
- [ ] Test robustness to compression, resizing and social-platform transformations.
- [ ] Publish methodology and limitations before exposing model scores.

## Milestone 4 — Social identity investigations
- [ ] Support user-submitted public profile URLs where platform terms permit.
- [ ] Compare public claims with independent sources.
- [ ] Report inconsistencies as leads for human review, not proof of fraud.

## Milestone 5 — Community release
- [ ] Publish documentation and contribution guide.
- [ ] Run independent security and privacy review.
- [ ] Release a tested public beta.
