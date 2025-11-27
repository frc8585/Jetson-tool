from dataclasses import dataclass
import numpy as np

@dataclass
class LocationData():
    timestamp: float
    position: np.ndarray  # 3D position vector
    orientation: np.ndarray  # Euler angles (pitch, yaw, roll)