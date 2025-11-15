from fastapi import APIRouter
from fastapi.responses import JSONResponse, StreamingResponse
import cv2
import io

from backend.services.camera_manager_service import save_camera_config, load_camera_config, get_camera_config, get_camera_img

router = APIRouter(prefix="/test", tags=["test"])


@router.get("/save")
async def test_get():
    save_camera_config()
    return JSONResponse(content={"message": "Camera config saved successfully."})

@router.get("/load")
async def test_get():
    load_camera_config()
    return JSONResponse(content={"message": "Camera config loaded successfully."})

@router.get("/get")
async def test_get():
    cameras = get_camera_config()
    result = [cam.model_dump(mode='json') for cam in cameras]
    return JSONResponse(content={"cameras": result})

@router.get("/frametest")
async def test_get_frame(camera_id: str):
    try:
        frame, timestamp = get_camera_img(camera_id)
        _, encoded_image = cv2.imencode(".jpg", frame)
        return StreamingResponse(io.BytesIO(encoded_image.tobytes()), media_type="image/jpeg")
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
    
@router.get("/update_threads")
async def update_threads():
    from backend.services import camera_manager_service
    camera_manager_service.update_camera_image_updater()
    return JSONResponse(content={"message": "Camera image updater threads updated."})