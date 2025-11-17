from enum import IntEnum
from typing import Optional
from pydantic import BaseModel
    
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