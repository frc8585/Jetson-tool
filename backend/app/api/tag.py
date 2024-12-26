from fastapi import APIRouter
import json
import threading

from app.services import data_processor
from app.services.Calibration import CameraCalibrator


tag_routes = APIRouter()

@tag_routes.get("/hello")
async def say_hello():
    return {"message": "Hello, FastAPI!"}

# 提供 API 以獲取最新的 AprilTag 檢測數據
@tag_routes.get("/apriltag/latest")
async def get_latest_data():
    return json.dumps(data_processor.get_latest_data().to_dict())

# 提供 API 以進行相機標定
@tag_routes.post("/calibrate")
async def calibrate_camera(num_images: int = 10):
    calibrator = CameraCalibrator()
    calibrator.run_calibration(num_images)
    return {"message": "Calibration completed"}