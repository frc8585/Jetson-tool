import numpy as np

class Config:
    def __init__(self, K, postion, orientation, isenable=False):
        self.isenable = isenable
        self.K = K
        self.postion = postion
        self.orientation = orientation
    def to_dict(self):
        return {
            "isenable": self.isenable,
            "K": self.K.tolist(),
            "postion": self.postion.tolist(),
            "orientation": self.orientation.tolist()
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


