from enum import IntEnum
import threading
import time
from typing import Optional
import base64
import cv2
from pydantic import BaseModel


class CameraImageBuffer:
    """
    """
    #TODO 製作影像儲存邏輯與架構
    def __init__(self):
        # 1. 
        self.condition = threading.Condition()
        
        # 2. 
        self.latest_frame = None
        self.timestamp = 0
        self.frame_id = -1
        
    def set(self, frame, timestamp):
        with self.condition:
            self.latest_frame = frame
            self.timestamp = timestamp
            self.frame_id += 1
            self.condition.notify_all()
            
    def wait_for_new_frame(self, last_seen_id: int):
        """
        """
        with self.condition:
            # 
            # 
            while self.frame_id == last_seen_id:
                # 
                self.condition.wait() 
            
            # 
            return self.latest_frame, self.timestamp, self.frame_id
    
    def get_nowait(self):
        """
        """
        with self.condition:
            return self.latest_frame, self.timestamp
    
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

class CameraConfig(BaseModel):
    # TODO: 製作相機設定相關參數
    pass

class CameraTagData(BaseModel):
    tag_id: int
    center: tuple[float, float]
    corners: list[tuple[float, float]]
    
class RecognitionResult(BaseModel):
    camera_id: str
    timestamp: float
    tags: list[CameraTagData]