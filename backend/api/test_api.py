from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, StreamingResponse
from backend.services.camera_manager_service import CameraManager
import cv2
import io

router = APIRouter(prefix="/test", tags=["test"])

# TODO 整理測試API並移除危險內容或併入一般功能

@router.get("/save")
async def test_save(request: Request):
    request.app.state.camera_manager.save_camera_config()
    return JSONResponse(content={"message": "Camera config saved successfully."})

@router.get("/load")
async def test_load(request: Request):
    request.app.state.camera_manager.load_camera_config()
    return JSONResponse(content={"message": "Camera config loaded successfully."})

@router.get("/get")
async def test_get(request: Request):
    cameras = request.app.state.camera_manager.get_camera_config()
    result = [cam.model_dump(mode='json') for cam in cameras]
    return JSONResponse(content={"cameras": result})

@router.get("/frametest")
async def test_get_frame(request: Request, camera_id: str):
    try:
        frame, _ = request.app.state.camera_manager.get_camera_img(camera_id)
        if frame is None:
            return JSONResponse(content={"error": "No frame available."}, status_code=204)
        _, encoded_image = cv2.imencode(".jpg", frame)
        return StreamingResponse(io.BytesIO(encoded_image.tobytes()), media_type="image/jpeg")
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
    