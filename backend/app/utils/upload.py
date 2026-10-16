from fastapi import HTTPException, UploadFile


DEFAULT_MAX_FILE_SIZE = 10 * 1024 * 1024
DEFAULT_ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
    "image/webp",
    "text/plain",
}


async def validate_upload(
    file: UploadFile,
    allowed_content_types: set[str] | None = None,
    max_file_size: int = DEFAULT_MAX_FILE_SIZE,
) -> UploadFile:
    if not file.filename:
        raise HTTPException(status_code=400, detail="A file is required")

    allowed_types = allowed_content_types or DEFAULT_ALLOWED_CONTENT_TYPES
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="File type is not allowed")

    content = await file.read(max_file_size + 1)
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")
    if len(content) > max_file_size:
        raise HTTPException(status_code=413, detail="Uploaded file is too large")

    await file.seek(0)
    return file