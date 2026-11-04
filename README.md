# EL-VERIFY

**Verify What You See. Trust What You Know.**

EL-VERIFY is a project to help people check digital content and understand the evidence behind it. We are starting with images and their provenance, then plan to add tools for checking sources, public identity claims and the history of digital files.

> **Current status:** The first MVP is live as a public demo. You can upload an image, review its technical details and check whether it contains C2PA Content Credentials. The demo does not detect AI-generated images or decide whether an image is real or fake. It is a demonstration service, not a production service.

**[Open the live demo](https://el-verify-demo.onrender.com/app/)**

## What you can do now

- Upload JPEG, PNG, WebP or TIFF images.
- View the image format, file size, dimensions and SHA-256 fingerprint.
- Review available EXIF metadata indicators.
- Check for C2PA Content Credentials using the official C2PA Python SDK.
- See whether credentials were found, are absent, or could not be read.
- Export a JSON report of the technical findings.

The report does not include the uploaded image, its original filename or raw EXIF values.

## What EL-VERIFY does not claim

The current MVP does not tell you whether an image is real, fake, AI-generated or manipulated. A missing credential does not mean an image has been edited. Even when credentials are present, that does not automatically prove that the content or the claims attached to it are true.

We want EL-VERIFY to show useful evidence and explain its limits, rather than give people a confident answer that the evidence cannot support.

## The bigger idea

The image checker is only the first part of EL-VERIFY. The wider project has five planned areas:

- **EL-VISION:** inspect images and, after proper testing, other media for useful technical and manipulation evidence.
- **EL-SOURCE:** help users check where content and claims came from, with links to supporting sources.
- **EL-IDENTITY:** help review claims made by public profiles using independent public information. This will not use facial recognition.
- **EL-TRACE:** help users understand file fingerprints, metadata and available provenance history.
- **EL-INTELLIGENCE:** bring findings from the different checks into one clear report that people can review.

These areas will be developed in stages. Most of them are still planned and are not available in the current demo.

**[See the full roadmap](docs/ROADMAP.md)** for the planned work, current progress and the safeguards we intend to follow.

## Run it locally

You need Python 3.10 or newer.

From the repository root:

```bash
cd backend
python -m venv .venv

# Windows
.venv\\Scripts\\activate

# macOS or Linux
source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/ to use the interface, or http://127.0.0.1:8000/docs to view the API documentation.

## API

- `GET /api/health`
- `POST /api/images/inspect`

The inspection endpoint accepts JPEG, PNG, WebP and TIFF images up to 10 MB.

Remote C2PA manifest fetching and OCSP network requests are disabled during inspection. This helps prevent an uploaded file from causing unexpected outbound network requests.

## Project structure

- `backend/` contains the FastAPI service and image inspection code.
- `frontend/` contains the browser interface.
- `docs/` contains the architecture, roadmap, deployment and responsible-use notes.
- `.github/workflows/` contains the automated checks.

## Try the demo or deploy your own

The public demo is available at **[el-verify-demo.onrender.com](https://el-verify-demo.onrender.com/app/)**. It may take a little time to wake up after being idle.

You can also [deploy your own copy to Render](https://render.com/deploy?repo=https://github.com/elnexi461-spec/EL-VERIFY). See [the deployment guide](docs/DEMO_DEPLOYMENT.md) for the steps.

## How we want to build it

- Show evidence and explain uncertainty.
- Do not treat a model score as a verdict.
- Do not treat missing metadata as proof of manipulation.
- Do not identify people or guess their identity from their faces.
- Respect privacy, platform rules and the rights of content owners.
- Keep users in control of the content they submit.

For more detail, see [Responsible Use](docs/RESPONSIBLE_USE.md), [Architecture](docs/ARCHITECTURE.md) and [C2PA notes](docs/C2PA.md).

## License

EL-VERIFY is released under the MIT License. See [LICENSE](LICENSE) for the full license text.
