# EL-VERIFY Roadmap

EL-VERIFY is being built to help people check digital content, understand where it came from, and review the claims made about it. The long-term goal is to bring several useful checks into one place and show the evidence behind each result.

This roadmap explains what is working now and what we want to build next. Planned features are not part of the current demo.

## 1. What works today: image evidence and provenance

- [x] FastAPI backend and browser-based interface.
- [x] Image upload for JPEG, PNG, WebP and TIFF.
- [x] File size, format, dimensions and image mode checks.
- [x] SHA-256 file fingerprint.
- [x] EXIF metadata indicators.
- [x] C2PA Content Credentials inspection with the official Python SDK.
- [x] Clear results when credentials are found, absent, unsupported or cannot be read.
- [x] Upload validation and image safety limits.
- [x] Temporary file cleanup and no default storage of uploaded images.
- [x] JSON evidence report export.
- [x] Tests for unsigned images and signed-image tampering.
- [x] Docker setup and a public demo.

The current version does not decide whether an image is real, fake, AI-generated or manipulated. It reports technical evidence and explains what that evidence can and cannot tell us.

## 2. EL-VISION: stronger media checks

The next step is to improve the way EL-VERIFY examines images and, later, other media.

- [ ] Improve the image evidence report and make findings easier to understand.
- [ ] Add support for more provenance and content credential cases.
- [ ] Research image and video manipulation detection using public, properly licensed datasets.
- [ ] Test detection methods against edited, compressed, resized and AI-generated media.
- [ ] Measure false positives and false negatives before showing any model result.
- [ ] Explore video inspection and frame-level evidence.

Any detection score will be shown as an indicator, not a final answer. We will publish the limits of each method and avoid claiming that a model can prove whether something is genuine.

## 3. EL-SOURCE: check sources and claims

This module will help users look into where a post, image or claim came from.

- [ ] Allow users to submit a public URL for review.
- [ ] Check domain details and available source information.
- [ ] Collect relevant public references and citations.
- [ ] Let users compare a claim with independent sources.
- [ ] Show which information came from the source, which came from the user, and what remains unknown.
- [ ] Add strict protections against unsafe links, private network access, redirects and DNS rebinding before any server-side URL fetching.

The aim is to help people investigate a source, not to label a website or publisher as trustworthy based on one check.

## 4. EL-IDENTITY: review public identity claims

This module is about checking claims made by public profiles and accounts. It is not facial recognition.

- [ ] Let users submit public profile links where access is permitted.
- [ ] Compare public profile claims with other independent public information.
- [ ] Highlight missing details or inconsistencies for a person to review.
- [ ] Provide links and evidence for each finding.
- [ ] Respect platform rules and avoid private data, account access or identity guesses based on faces.

A mismatch will be presented as something worth checking, not proof that someone is fake or dishonest.

## 5. EL-TRACE: follow the history of digital files

The MVP already creates a SHA-256 fingerprint and checks available image metadata. We want to build on that foundation.

- [x] Create a SHA-256 fingerprint for an inspected image.
- [x] Show available metadata indicators.
- [ ] Improve the way users compare file fingerprints and evidence reports.
- [ ] Explore file history and provenance records where reliable evidence is available.
- [ ] Make it easier to see what is known about a file and what cannot be confirmed.

## 6. EL-INTELLIGENCE: bring the evidence together

This module will help users understand findings from the other parts of EL-VERIFY.

- [ ] Combine evidence from image, source, identity-claim and file-history checks.
- [ ] Produce a clear report with sources, findings and unknowns.
- [ ] Explain why a finding matters in plain language.
- [ ] Keep human review at the centre of sensitive decisions.
- [ ] Make it possible to challenge or correct an incorrect report.

The goal is not to produce a single unexplained trust score. Users should be able to see the evidence behind every important finding.

## 7. Security, privacy and public release

These are ongoing requirements, not features to leave until the end.

- [x] Validate uploaded file types, sizes and image dimensions.
- [x] Disable remote C2PA manifest and OCSP fetching during image inspection.
- [x] Avoid keeping uploaded media after inspection.
- [x] Exclude raw EXIF values and image bytes from exported reports.
- [ ] Review URL-fetching security before releasing source checks.
- [ ] Arrange an independent security and privacy review.
- [ ] Improve accessibility and usability based on user feedback.
- [ ] Publish evaluation methods, known limitations and test results.
- [ ] Prepare a wider public beta after the security review.

## Our approach

We will build this in stages, test each part, and be open about what is ready and what is still being researched. EL-VERIFY should help people make better-informed decisions. It should not make serious accusations or claim certainty when the evidence is incomplete.

The roadmap may change as we test the project and learn from users and reviewers.
