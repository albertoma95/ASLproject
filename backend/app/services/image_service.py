import os
from fastapi import UploadFile

UPLOAD_DIR = "uploads"

async def save_image(file: UploadFile) -> str:
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    filepath = os.path.join(UPLOAD_DIR, file.filename)

    with open(filepath, "wb") as f:
        content = await file.read()
        f.write(content)

    return file.filename
