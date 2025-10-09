from enum import IntEnum
import time
from typing import Optional
import base64
import cv2
from pydantic import BaseModel


class CameraImage:
    pass
    #TODO 製作影像儲存邏輯與架構
    
class BackendType(IntEnum):
    OTHER = -1
    LINUX_UDEV = 0

class Camera(BaseModel):
    name: str
    camera_id: str
    backend: BackendType
    path: str
    backend_detail: Optional[str] = None

    def get_all(self):
        return {
            "name": self.name,
            "camera_id": self.camera_id,
            "backend": self.backend,
            "path": self.path,
            "backend_detail": self.backend_detail,
        }
