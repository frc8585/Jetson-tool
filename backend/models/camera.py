import time
from typing import Optional
import base64
import cv2


class CameraData:
    def __init__(self, timestamp, img: Optional[cv2.Mat]):
        self.timestamp = timestamp
        self.img = img

    def get_all(self, encode_image: bool = False):
        """Return serializable representation of camera data.

        By default `img` is not included (set to None). If `encode_image=True`
        the image will be encoded to JPEG and returned as a base64 string.
        This avoids returning raw OpenCV Mat objects which are not JSON serializable.
        """
        img_field = None
        if self.img is not None and encode_image:
            # Encode image to JPEG bytes then base64 to include in JSON
            success, buf = cv2.imencode('.jpg', self.img)
            if success:
                img_field = base64.b64encode(buf.tobytes()).decode('ascii')

        return {
            "timestamp": self.timestamp,
            "img": img_field,
        }
    
class BackendType:
    OTHER = -1
    LINUX_UDEV = 0
    WINDOWS_DSHOW = 1

class Camera:
    def __init__(self, name: str, camera_id: str, backend: BackendType, path: str, backend_detail: str = None, camera_data: CameraData = None):
        self.name = name
        self.camera_id = camera_id
        self.backend = backend
        self.path = path
        self.backend_detail = backend_detail
        self.camera_data = camera_data

    def get_all(self, encode_image: bool = False):
        return {
            "name": self.name,
            "camera_id": self.camera_id,
            "backend": self.backend,
            "path": self.path,
            "backend_detail": self.backend_detail,
            "camera_data": self.camera_data.get_all(encode_image=encode_image) if self.camera_data else None,
        }
    
    def set_img(self, img: cv2.Mat):
        if self.camera_data is None:
            self.camera_data = CameraData(time.time(), img)
        else:
            self.camera_data.img = img
            self.camera_data.timestamp = time.time()
