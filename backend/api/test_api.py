from fastapi import APIRouter
from fastapi.responses import JSONResponse

from backend.services.camera_manager_service import save_camera_config, load_camera_config, get_camera_config

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
