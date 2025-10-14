from fastapi import APIRouter
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from backend.models.camera import Camera
from backend.services import camera_manager_service
from backend.utils.camera import get_all_connected_cameras

router = APIRouter(prefix="/camera", tags=["camera"])

# TODO 整理各種API呼叫與需要甚麼工具函式
@router.get("/cameras")
async def get_cameras():
    # TODO 撰寫API註解
    return JSONResponse(content=jsonable_encoder(get_all_connected_cameras()))

@router.get("/config")
async def get_camera_config():
    return JSONResponse(content=jsonable_encoder(camera_manager_service.get_camera_config()))

@router.post("/add_camera")
async def add_camera(camera: Camera):
    try:
        camera_manager_service.add_camera(camera)
        return JSONResponse(content={"message": "Camera added successfully."}, status_code=201)
    except ValueError as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)
    

@router.delete("/remove_camera/{camera_id:path}")
async def remove_camera(camera_id: str):
    try:
        camera_manager_service.remove_camera(camera_id)
        return JSONResponse(content={"message": "Camera removed successfully."})
    except ValueError as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)