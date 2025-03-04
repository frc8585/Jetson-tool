import wmi
import cv2
import numpy as np
import time
import pythoncom
import platform

from pygrabber.dshow_graph import FilterGraph
from app.models.Camera import Camera, Config
from config import Camera_Config

class Camera_tool:

    def get_all_camera(self):
        camera_info = []
        system = platform.system()

        if system == "Windows":
            pythoncom.CoInitialize()
            w = wmi.WMI()
            graph = FilterGraph()

            devices = graph.get_input_devices()  # 獲取所有可用相機名稱
            for index, name in enumerate(devices):
                query = "SELECT * FROM Win32_PnPEntity WHERE Name LIKE '%{}%'".format(name)
                cameraid = w.query(query)
                camera_id = cameraid[0].DeviceID if cameraid else None

                camera_info.append(Camera(
                    index=index,
                    name=name,
                    id=camera_id,
                    config=None
                ))

                # 獲取相機設定
                camera_config = Camera_Config()
                config = camera_config.get_camera_by_id(camera_id)
                if config:
                    config = config["config"]
                if config:
                    camera_info[-1].config = Config(
                        K=np.array(config["K"]),
                        postion=np.array(config["postion"]),
                        orientation=np.array(config["orientation"]),
                        isenable=config["isenable"]
                    )

            graph.stop()

        elif system == "Linux":
            import subprocess

            result = subprocess.run(['v4l2-ctl', '--list-devices'], stdout=subprocess.PIPE)
            devices = result.stdout.decode().split('\n\n')
            for index, device in enumerate(devices):
                lines = device.split('\n')
                if len(lines) > 1:
                    name = lines[0]
                    path = lines[1].strip()
                    camera_info.append(Camera(
                        index=index,
                        name=name,
                        id=path,
                        config=None
                    ))

                    # 獲取相機設定
                    camera_config = Camera_Config()
                    config = camera_config.get_camera_by_id(path)
                    if config:
                        config = config["config"]
                    if config:
                        camera_info[-1].config = Config(
                            K=np.array(config["K"]),
                            postion=np.array(config["postion"]),
                            orientation=np.array(config["orientation"]),
                            isenable=config["isenable"]
                        )

        # 添加 ZED 相機
        camera_info.append(Camera(
            index = "zed_left",
            name = "zed_left",
            id = "zed_left",
            config = None
        ))

        camera_info.append(Camera(
            index="zed_right",
            name="zed_right",
            id="zed_right",
            config=None
        ))

        return camera_info

    def get_camera_by_id(self, id):
        cameras = self.get_all_camera()
        for camera in cameras:
            if camera.id == id:
                return camera
        return None

    def get_camera_by_index(self, index):
        cameras = self.get_all_camera()
        for camera in cameras:
            if camera.index == index:
                return camera
        return None

    def dict_to_camera(self, dict):
        return Camera(dict["index"], dict["name"], dict["id"], dict["config"] if "config" in dict else None)

