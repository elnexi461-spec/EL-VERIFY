from fastapi import APIRouter, File, HTTPException, UploadFile

from app.services.image_inspection import inspect_image

router = APIRouter(prefix="/images", tags=["image inspection"])

MAX_UPLOAD_BYTES = 10 * 1024 * 1024
ALLOWED_CONTENT_TYPES = {
    "image/jpeg": "JPEG",
    "image/png": "PNG",
    "image/webp": "WEBP",
    "image/tiff": "TIFF",
}


@router.post("/inspect")
async def inspect_uploaded_image(file: UploadFile = File(...)):
    expected_format = ALLOWED_CONTENT_TYPES.get(file.content_type or "")
    if expected_format is None:
        raise HTTPException(status_code=415, detail="Unsupported image type.")

    content = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="Image exceeds the 10 MB limit.")

    try:
        result = inspect_image(content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if result["format"] != expected_format:
        raise HTTPException(
            status_code=415,
            detail="The uploaded file content does not match its declared image type.",
        )
    return result
