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
        # 使用 os.path.join 構建跨平台路徑
        self.camera_json_path = os.path.join('backend', 'public', 'camera', 'camera.json')
        with open(self.camera_json_path, 'r') as jsonFile:
            self.__camera = json.load(jsonFile)

    def get_all_camera(self):
        return self.__camera
    
    def remove_camera(self, camera):
        if camera in self.__camera:
            self.__camera.remove(camera)
        with open(self.camera_json_path, 'w') as jsonFile:
            json.dump(self.__camera, jsonFile)

    def add_camera(self, camera):
        self.__camera.append(camera)
        with open(self.camera_json_path, 'w') as jsonFile:
            json.dump(self.__camera, jsonFile)

class Field:
    def __init__(self):
        self.__field = {}
        # 使用 os.path.join 構建跨平台路徑
        field_dir = os.path.join('backend', 'public', 'Field')
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