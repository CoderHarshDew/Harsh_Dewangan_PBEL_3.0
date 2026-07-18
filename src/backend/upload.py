from fastapi import UploadFile, HTTPException

MAX_FILE_SIZE = 500 * 1024 * 1024


async def validate_upload(file: UploadFile):
    """Validates an uploaded file. Checks:

    If file size <= MAX_FILE_SIZE

    If file is CSV."""

    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")

    size = 0

    while chunk := await file.read(1024 * 1024):
        size += len(chunk)

        if size > MAX_FILE_SIZE:
            raise HTTPException(status_code=413,detail="File size exceeds 500 MB limit")

    await file.seek(0)

    return file