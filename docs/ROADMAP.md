# EL-VERIFY Roadmap

## Milestone 0 — Foundation
- [x] Establish project scope and responsible-use principles.
- [x] Create initial FastAPI service.
- [x] Add basic image metadata and hash inspection.
- [x] Add starter tests.
- [x] Publish initial repository scaffold.
- [ ] Choose and add an open-source license.

## Milestone 1 — Image evidence
- [x] Return file size, dimensions, format, SHA-256 and metadata indicators.
- [x] Validate decoded image format against declared upload content type.
- [x] Add upload size and image pixel-count limits.
- [x] Add tests for invalid files and unsupported formats.
- [ ] Run the test suite and add continuous integration.
- [ ] Add safe metadata export.
- [ ] Research and document C2PA / Content Credentials verification.
- [ ] Document metadata and provenance limitations.

## Milestone 2 — Source verification
- [ ] Build safe URL parsing and domain information checks.
- [ ] Add source citation and evidence capture.
- [ ] Add protections against private-network and localhost URL access.

## Milestone 3 — Synthetic media research
- [ ] Select public, licensed evaluation datasets.
- [ ] Benchmark candidate models for false positives and false negatives.
- [ ] Publish methodology and limitations before exposing model scores.

## Milestone 4 — Social identity investigations
- [ ] Support user-submitted public profile URLs where platform terms permit.
- [ ] Compare public claims with independent sources.
- [ ] Report inconsistencies as leads for human review, not proof of fraud.

## Milestone 5 — Community release
- [ ] Publish documentation and contribution guide.
- [ ] Run security and privacy review.
- [ ] Release a tested public beta.
