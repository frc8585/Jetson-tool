from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from backend.models.camera import Camera
from backend.utils.camera import get_all_connected_cameras

router = APIRouter(prefix="/camera", tags=["camera"])

# TODO 整理各種API呼叫與需要甚麼工具函式
@router.get("/get_all_cameras")
async def get_all_cameras():
    # TODO 撰寫API註解
    return JSONResponse(content=jsonable_encoder(get_all_connected_cameras()))

@router.get("/get_camera_config")
async def get_camera_config(request: Request):
    return JSONResponse(content=jsonable_encoder(request.app.state.camera_manager.get_camera_config()))

@router.post("/set_camera_config")
async def set_camera_config(request: Request, camera: Camera):
    try:
        request.app.state.camera_manager.add_camera(camera)
        return JSONResponse(content={"message": "Camera added successfully."}, status_code=201)
    except ValueError as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)
    

@router.delete("/remove_camera_config/{camera_id:path}")
async def remove_camera_config(request: Request, camera_id: str):
    try:
        request.app.state.camera_manager.remove_camera(camera_id)
        return JSONResponse(content={"message": "Camera removed successfully."})
    except ValueError as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)