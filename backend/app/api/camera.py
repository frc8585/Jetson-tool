from fastapi import APIRouter
from pydantic import BaseModel
import json
import threading

from app.utils import camera_tool
from config import Camera
from app.models.Camera import Config

class setCamera(BaseModel):
    id: str
    K: list
    postion: list
    orientation: list

camera_routes = APIRouter()
camera_config = Camera()

@camera_routes.get("/hello")
async def say_hello():
    return {"message": "Hello, Camera!"}

# 提供 API 以獲取最新的 AprilTag 檢測數據
@camera_routes.get("/get_camera")
async def get_camera():
    return camera_tool.get_all_camera()

@camera_routes.post("/set_camera")
async def set_camera(set_camera: setCamera):
    camera = camera_tool.get_camera_by_id(set_camera.id)
    camera.config = Config(set_camera.K, set_camera.postion, set_camera.orientation)
    return camera_config.add_camera(camera)
