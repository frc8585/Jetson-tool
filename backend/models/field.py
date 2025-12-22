from typing import List, Optional
from pydantic import BaseModel

class TagConfig(BaseModel):
    id: int
    size: float  # Tag size in meters
    position: List[float]  # [x, y, z] in meters
    rotation: List[float]  # [roll, pitch, yaw] in degrees

class FieldConfig(BaseModel):
    name: str
    tags: List[TagConfig]
