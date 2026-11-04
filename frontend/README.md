# EL-VERIFY Web Interface

A lightweight browser interface for the EL-VISION image inspection API. It uses plain HTML, CSS and JavaScript, so no Node build step is required.

## Run

Start the FastAPI backend from the backend directory:

    pip install -r requirements.txt
    uvicorn app.main:app --reload

Open http://127.0.0.1:8000/app/.

The frontend uploads images to POST /api/images/inspect and renders the returned evidence report. Files are processed in memory and in a temporary file for C2PA parsing; the temporary file is deleted after inspection.

## Current limitations

- No accounts, report history or persistent media storage.
- No AI-generated image classifier or deepfake verdict.
- C2PA verification depends on the official C2PA Python SDK and its trust configuration.
- The interface reports technical findings, not the truth of a depicted scene or provenance assertion.
