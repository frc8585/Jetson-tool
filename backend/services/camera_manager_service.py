import cv2
import yaml

from backend.models import Camera
from backend.utils import camera as camera_utils
import os

CAMERA_CONFIG_DIR = os.path.join("backend", "config", "camera.yml")
#test_camera = Camera(name="Test Camera", camera_id="test_001", backend=0, path="/path/to/test_camera", backend_detail="")
cameras = []
camera_cap = {}

def config_reset():
    os.makedirs(os.path.dirname(CAMERA_CONFIG_DIR), exist_ok=True)
    with open(CAMERA_CONFIG_DIR, "w") as f:
        yaml.safe_dump({"cameras": []}, f)



def load_camera_config():
    try:
        with open(CAMERA_CONFIG_DIR, "r") as f:
            config = yaml.safe_load(f)
            if config is None:
                config_reset()
                return
            for cam in config.get("cameras", []):
                if not cam in cameras:
                    cameras.append(Camera(**cam))
    except Exception as e:
        print(f"Error loading camera config: {e}")

def save_camera_config():
    try:
        if not os.path.exists(CAMERA_CONFIG_DIR):
            config_reset()
        with open(CAMERA_CONFIG_DIR, "w") as f:
            config = {"cameras": [cam.model_dump(mode='json') for cam in cameras]}
            yaml.safe_dump(config, f)
    except Exception as e:
        print(f"Error saving camera config: {e}")

def set_cap_table():
    for cam in cameras:
        try:
            cap = camera_utils.start_camera_cap(cam)
            # TODO: 把解析度移到camera設定裡
            # 測試用
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            camera_cap[cam.camera_id] = cap
        except Exception as e:
            print(f"Error initializing camera {cam.camera_id}: {e}")

def get_camera_config():
    return cameras

def get_camera_img(camera_id):
    if camera_id not in camera_cap:
        raise ValueError(f"Camera with ID {camera_id} not initialized.")

    cap = camera_cap[camera_id]
    ret, frame = cap.read()
    if not ret:
        raise ValueError(f"Failed to capture image from camera {camera_id}")

    return frame

# -----------------初始化------------------
# 1. 檢查 config 檔案是否存在
if not os.path.exists(CAMERA_CONFIG_DIR):
    config_reset()

# # 2. 載入 config 檔案
load_camera_config()
# # 3. 初始化 camera_cap
set_cap_table()