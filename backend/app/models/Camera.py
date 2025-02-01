import numpy as np

class Config:
    def __init__(self, K, postion, orientation):
        self.K = K
        self.postion = postion
        self.orientation = orientation
    def to_dict(self):
        return {
            "K": self.K,
            "postion": self.postion,
            "orientation": self.orientation
        }

class Camera:
    def __init__(self, index, name, id, config:Config=None):
        self.index = index
        self.name = name
        self.id = id
        self.config = config

    def to_dict(self):
        return {
            "index": self.index,
            "name": self.name,
            "id": self.id,
            "config": self.config.to_dict() if self.config else None
        }


