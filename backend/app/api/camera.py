import asyncio
import cv2
from fastapi import APIRouter, WebSocket
from pydantic import BaseModel
import json
import threading

from app.utils import camera_tool
from config import Camera_Config
from app.models.Camera import Config
from app.services import image_processing


camera_routes = APIRouter()
camera_config = Camera_Config()

# 測試用
@camera_routes.get("/hello")
async def say_hello():
    return {"message": "Hello, Camera!"}

# 保存活躍的 WebSocket 連接
active_connections = {}

# WebSocket 連接管理
@camera_routes.websocket("/ws/{camera_id}")
async def websocket_endpoint(websocket: WebSocket, camera_id: str):
    await websocket.accept()
    
    # 將連接添加到活躍連接列表
    if camera_id not in active_connections:
        active_connections[camera_id] = []
    active_connections[camera_id].append(websocket)
    
    try:
        camera = camera_tool.get_camera_by_id(camera_id)
        if camera is None:
            await websocket.close()
            return
            
        while True:
            # 直接從相機工具獲取編碼後的畫面
            frame = image_processing.get_frame(camera.index)  # 假設相機物件有此方法

            if frame is not None:
                _, buffer = cv2.imencode('.jpg', frame)
                await websocket.send_bytes(buffer.tobytes())
            await asyncio.sleep(0.03)  # 10 FPS
            
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        # 移除連接
        active_connections[camera_id].remove(websocket)
        if not active_connections[camera_id]:
            del active_connections[camera_id]

# 獲取所有相機
@camera_routes.get("/get_camera")
async def get_camera():
    l = camera_tool.get_all_camera()
    for i, v in enumerate(l):
        l[i] = v.to_dict()
    return l

# 設定相機設定
class setCamera(BaseModel):
    id: str
    isenable: bool
    K: list
    postion: list
    orientation: list

@camera_routes.post("/set_camera")
async def set_camera(set_camera: setCamera):
    camera = camera_tool.get_camera_by_id(set_camera.id)
    camera.config = Config(set_camera.K, set_camera.postion, set_camera.orientation)
    camera.config.isenable = set_camera.isenable
    result = camera_config.add_camera(camera)
    #刷新影像處理相機設定
    image_processing.reload_camera()
    return result

# 相機標定功能
class Calibrate_config(BaseModel):
    id: str
    row: int
    col: int
    size: float # mm

@camera_routes.post("/calibrate")
async def calibrate(calibrate_config: Calibrate_config):
    camera = camera_tool.get_camera_by_id(calibrate_config.id)
    camera_tool.calibrate(camera, calibrate_config.row, calibrate_config.col, calibrate_config.size)
    return camera_config.add_camera(camera)
