# Deploy the EL-VERIFY demo

The public demonstration is available at https://el-verify-demo.onrender.com/app/. This repository also includes a Render Blueprint for creating a separate instance.

## Deploy

1. Sign in to Render and connect the GitHub account that can access `elnexi461-spec/EL-VERIFY`.
2. Open the Render Blueprint creation flow: https://dashboard.render.com/blueprints
3. Select this repository and the `main` branch.
4. Render should detect the root `render.yaml`. Review the service and choose **Apply**.
5. Wait for the Docker build and first deploy to finish. The free instance can take a little time to wake up.
6. Open the generated `onrender.com` URL. The app should redirect to `/app/`.
7. Confirm `/api/health` returns a healthy response, then upload a JPG or PNG you are allowed to inspect.

## What the public demo does

- Accepts JPEG, PNG, WEBP and TIFF images up to 10 MB.
- Reports file properties, SHA-256 and selected metadata indicators.
- Checks for embedded C2PA Content Credentials and reports the SDK validation state when available.
- Allows a JSON evidence report to be exported in the browser.

## Important limitations

- This is a demonstration deployment, not a production service.
- Render's free web services sleep after 15 minutes without traffic and can take around a minute to wake up.
- The free service has an ephemeral filesystem. EL-VERIFY does not provide persistent image storage or user accounts.
- Do not upload private, sensitive or confidential images. Only upload files you are authorized to submit.
- The demo does not decide whether an image is real, fake, AI-generated or misleading. Missing credentials are not proof of manipulation.
- A public endpoint can receive unsolicited traffic. Keep the demo temporary, monitor usage and disable the service when it is no longer needed. Do not use this free deployment for production workloads.

## Automated upload safeguards

The backend test suite includes API-level checks for unsupported MIME types (415), files larger than 10 MB (413), and mismatches between a declared MIME type and the actual decoded image format (415). These checks exercise the API directly, because the browser file picker intentionally filters out unsupported file types.

## After deployment

The live URL is recorded in the project README. Re-test the normal upload and JSON export flow after significant backend changes. A successful deployment or health check alone is not enough to establish production readiness.
