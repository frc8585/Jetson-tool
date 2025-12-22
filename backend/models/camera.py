from dataclasses import dataclass
from enum import IntEnum
from typing import Optional
import numpy as np
from pydantic import BaseModel
    
class BackendType(IntEnum):
    OTHER = -1
    LINUX_UDEV = 0

class CameraConfig(BaseModel):
    # 3x3 Intrinsic Matrix
    K: list[list[float]] 
    # Distortion Coefficients (k1, k2, p1, p2, k3...)
    D: Optional[list[float]] = None 
    size: tuple[int, int] # (width, height)
    fps: Optional[float] = None
    
    def get_all(self):
        return {
            "K": self.K,
            "D": self.D,
            "size": self.size,
            "fps": self.fps,
        }


class Camera(BaseModel):
    name: str
    camera_id: str
    backend: BackendType
    path: str
    backend_detail: Optional[str] = None
    config: Optional[CameraConfig] = None

    def get_all(self):
        return {
            "name": self.name,
            "camera_id": self.camera_id,
            "backend": self.backend,
            "path": self.path,
            "backend_detail": self.backend_detail,
            "config": self.config.model_dump(mode="json") if self.config else None,
        }

@dataclass
class CameraTagData():
    tag_id: int
    center: tuple[float, float]
    corners: np.ndarray
    
@dataclass
class RecognitionResult():
    camera_id: str
    timestamp: float
    tags: list[CameraTagData]