import json
import os
import numpy as np
from scipy.spatial.transform import Rotation as R
from backend.models.field import FieldConfig, TagConfig

FIELD_CONFIG_PATH = os.path.join("backend", "config", "field.json")

class FieldManager:
    def __init__(self, config_path=FIELD_CONFIG_PATH):
        self.config_path = config_path
        self.field_data: FieldConfig = None
        self.tag_corners_cache = {}  # Cache for calculated corners: tag_id -> np.ndarray
        self.load_field_config()

    def load_field_config(self):
        """Load field configuration from JSON file."""
        if not os.path.exists(self.config_path):
            print(f"Field config not found at {self.config_path}, creating default.")
            self._create_default_config()
        
        try:
            with open(self.config_path, 'r') as f:
                data = json.load(f)
                self.field_data = FieldConfig(**data)
                self._precompute_corners()
                print(f"Loaded field '{self.field_data.name}' with {len(self.field_data.tags)} tags.")
        except Exception as e:
            print(f"Error loading field config: {e}")
            self.field_data = FieldConfig(name="Error", tags=[])

    def _create_default_config(self):
        """Create a default field config file."""
        default_config = {
            "name": "Default Field",
            "tags": []
        }
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(default_config, f, indent=4)

    def _precompute_corners(self):
        """Pre-calculate world coordinates for all tag corners."""
        self.tag_corners_cache = {}
        for tag in self.field_data.tags:
            self.tag_corners_cache[tag.id] = self._calculate_tag_corners(tag)

    def _calculate_tag_corners(self, tag: TagConfig) -> np.ndarray:
        """
        Calculate the 4 corners of the tag in world space.
        Order: Bottom-Left, Bottom-Right, Top-Right, Top-Left (Counter-Clockwise from BL)
        OR standard AprilTag order: (-x, -y), (x, -y), (x, y), (-x, y) relative to center?
        AprilTag detector usually returns corners in counter-clockwise order starting from bottom-left?
        Let's assume standard: 
        0: (-s/2, -s/2)
        1: ( s/2, -s/2)
        2: ( s/2,  s/2)
        3: (-s/2,  s/2)
        (in tag's local frame)
        """
        s = tag.size / 2.0
        # Local corners in tag frame (z=0)
        local_corners = np.array([
            [-s, -s, 0],
            [ s, -s, 0],
            [ s,  s, 0],
            [-s,  s, 0]
        ])

        # Rotation
        # Assuming rotation is [roll, pitch, yaw] in degrees
        r = R.from_euler('xyz', tag.rotation, degrees=True)
        rotation_matrix = r.as_matrix()

        # Transform to world
        # World = R * Local + T
        world_corners = np.dot(local_corners, rotation_matrix.T) + np.array(tag.position)
        
        return world_corners

    def get_tag_corners(self, tag_id: int) -> np.ndarray:
        """Get the world coordinates of the tag corners."""
        return self.tag_corners_cache.get(tag_id)

    def get_all_tags(self):
        return self.field_data.tags
