import queue
import cv2
import yaml

from backend.models import Camera
from backend.utils import camera as camera_utils
from backend.threads.camera_image_threads import CameraImageThread
import os

CAMERA_CONFIG_DIR = os.path.join("backend", "config", "camera.yml")
#test_camera = Camera(name="Test Camera", camera_id="test_001", backend=0, path="/path/to/test_camera", backend_detail="")
cameras = []
camera_cap = {}
camera_image = {}
camera_threads = {}
    
def set_image(camera_id, image, timestamp):
    camera_image[camera_id] = (image, timestamp)
    
def update_camera_image_updater():
    for cam in cameras:
        if camera_threads.get(cam.camera_id) is not None:
            camera_threads[cam.camera_id].stop()
            camera_threads[cam.camera_id].join()
            camera_threads[cam.camera_id] = None
        
        cap = camera_cap.get(cam.camera_id)
        if cap is None:
            print(f"Camera with ID {cam.camera_id} not initialized.")
            continue
        buffers = queue.Queue(maxsize=1)
        camera_image[cam.camera_id] = buffers
        thread = CameraImageThread(cap, buffers)
        thread.start()
        camera_threads[cam.camera_id] = thread

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
            for cam_dict in config.get("cameras", []):
                # 檢查 camera_id 是否已存在，避免重複加入
                if not any(c.camera_id == cam_dict.get("camera_id") for c in cameras):
                    cameras.append(Camera(**cam_dict))
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

            camera_cap[cam.camera_id] = cap
        except Exception as e:
            print(f"Error initializing camera {cam.camera_id}: {e}")

def get_camera_config():
    return cameras

def get_camera_img(camera_id):
    buffers = camera_image.get(camera_id)
    if buffers is None:
        raise ValueError(f"No image buffer found for camera ID {camera_id}")
    frame, timestamp = buffers.get() if not buffers.empty() else (None, None)

    return frame, timestamp

# --------------- 對外功能 -----------------
def add_camera(camera: Camera):
    if any(cam.camera_id == camera.camera_id for cam in cameras):
        raise ValueError(f"Camera with ID {camera.camera_id} already exists.")
    
    try:
        cap = camera_utils.start_camera_cap(camera)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        camera_cap[camera.camera_id] = cap

        cameras.append(camera)
        save_camera_config()
    except Exception as e:
        raise ValueError(f"Failed to initialize camera {camera.camera_id}: {e}")
    
def remove_camera(camera_id):
    for cam in cameras:
        if cam.camera_id == camera_id:
            cameras.remove(cam)
            break
    else:
        raise ValueError(f"Camera with ID {camera_id} not found.")
    
    cap = camera_cap.pop(camera_id, None)
    cap.release() if cap else None
    save_camera_config()


# -----------------初始化------------------
# 1. 檢查 config 檔案是否存在
if not os.path.exists(CAMERA_CONFIG_DIR):
    config_reset()

# # 2. 載入 config 檔案
load_camera_config()
# # 3. 初始化 camera_cap
set_cap_table()