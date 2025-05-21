from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
from app.services.image_service import save_image

router = APIRouter()

# @router.post("/upload/")
# async def upload_image(file: UploadFile = File(...)):
#     filename = await save_image(file)
#     return {"filename": filename}

image_counter = 0

@router.post("/upload/")
async def upload_image(file: UploadFile = File(...)):
    global image_counter
    image_counter += 1
    return JSONResponse(content={"image_number": image_counter})