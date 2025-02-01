from fastapi import APIRouter
import json
import threading

from app.utils import camera_tool

camera_routes = APIRouter()

@camera_routes.get("/hello")
async def say_hello():
    return {"message": "Hello, Camera!"}

# 提供 API 以獲取最新的 AprilTag 檢測數據
@camera_routes.get("/get_camera")
async def get_camera():
    return camera_tool.get_all_camera()

