from fastapi import APIRouter, UploadFile, File
from app.services.image_service import save_image

router = APIRouter()

@router.post("/upload/")
async def upload_image(file: UploadFile = File(...)):
    filename = await save_image(file)
    return {"filename": filename}
