import cv2
import yaml

from backend.models import Camera
import os

CAMERA_CONFIG_DIR = os.path.join("backend", "config", "camera.yml")
#test_camera = Camera(name="Test Camera", camera_id="test_001", backend=0, path="/path/to/test_camera", backend_detail="")
camera = []



def load_camera_config():
    try:
        with open(CAMERA_CONFIG_DIR, "r") as f:
            config = yaml.safe_load(f)
            for cam in config.get("cameras", []):
                if not cam in camera:
                    camera.append(Camera(**cam))
    except Exception as e:
        print(f"Error loading camera config: {e}")

def save_camera_config():
    try:
        with open(CAMERA_CONFIG_DIR, "w") as f:
            config = {"cameras": [cam.model_dump(mode='json') for cam in camera]}
            yaml.safe_dump(config, f,)
    except Exception as e:
        print(f"Error saving camera config: {e}")

def get_camera_config():
    return camera