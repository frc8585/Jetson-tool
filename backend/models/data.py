from dataclasses import dataclass, field
from typing import Optional, List
import numpy as np

@dataclass
class LocationData:
    """單一相機的位置觀測資料"""
    timestamp: float
    position: np.ndarray  # 3D position vector [x, y, z]
    orientation: np.ndarray  # Euler angles [pitch, yaw, roll]
    camera_id: str  # 來源相機 ID
    num_tags: int  # 使用的 Tag 數量
    tag_ids: List[int] = field(default_factory=list)  # Tag ID 列表
    error: Optional[float] = None  # PnP 重投影誤差（可選）