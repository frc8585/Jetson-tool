import os
import json
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    @property
    def APP_NAME(self) -> str:
        return "Jetson tool"

    @property
    def APP_VERSION(self) -> str:
        return "0.0.1"

    @property
    def HOST(self) -> str:
        return "0.0.0.0"

    @property
    def PORT(self) -> int:
        return int(os.getenv("PORT", 8000))

settings = Settings()

class Camera:
    def __init__(self):
        with open('backend/public/camera/camera.json', 'r') as jsonFile:
            self.__camera = json.load(jsonFile)

    def get_camera(self):
        return self.__camera
    
    def set_camera(self, camera):
        self.__camera = camera
        with open('public/camera/camera.json', 'w') as jsonFile:
            json.dump(camera, jsonFile)

class Field:
    def __init__(self):
        self.__field = {}
        field_dir = 'backend\public\Field'
        for filename in os.listdir(field_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(field_dir, filename)
                with open(filepath, 'r') as jsonFile:
                    key = os.path.splitext(filename)[0]
                    self.__field[key] = json.load(jsonFile)

    def get_field(self):
        return self.__field

    def get_field_by_key(self, key):
        return self.__field.get(key)