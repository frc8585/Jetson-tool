from fastapi import APIRouter
import json
import threading

from app.services import data_processor

tag_routes = APIRouter()

@tag_routes.get("/hello")
async def say_hello():
    return {"message": "Hello, FastAPI!"}

# 提供 API 以獲取最新的 AprilTag 檢測數據
@tag_routes.get("/apriltag/latest")
async def get_latest_data():
    return json.dumps(data_processor.get_latest_data().to_dict())
