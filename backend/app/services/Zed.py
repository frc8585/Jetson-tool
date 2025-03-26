import cv2
import numpy as np
import pyzed.sl as sl

from app.services import detector, data_processor
from app.models.Camera import Camera, Config
from config import Camera_Config, Field

class Zed:
    def __init__(self):
        self.zed = sl.Camera()
        self.init = sl.InitParameters()
        self.left_image = sl.Mat()
        self.right_image = sl.Mat()
        self.field = np.array(Field().get_field_by_key('2025').get("Field"))

    def Setting(self):
        # 獲取相機資訊
        camera_info = self.zed.get_camera_information()
        cam_config = camera_info.camera_configuration  # 相機配置
        calib_params = cam_config.calibration_parameters  # 校正參數

        # 內部參數矩陣 (K)
        K_left = np.array([
            [calib_params.left_cam.fx, 0, calib_params.left_cam.cx],
            [0, calib_params.left_cam.fy, calib_params.left_cam.cy],
            [0, 0, 1]
        ])

        K_right = np.array([
            [calib_params.right_cam.fx, 0, calib_params.right_cam.cx],
            [0, calib_params.right_cam.fy, calib_params.right_cam.cy],
            [0, 0, 1]
        ])



        # 顯示結果
        print("左相機內部參數矩陣 K:\n", K_left)
        print("右相機內部參數矩陣 K:\n", K_right)

        camera_l = Camera(
            id="zed_left",
            index="zed_left",
            name="ZED Left",
            config=Config(
                isenable=True,
                K=K_left,
                postion=np.array([0, 0, 0]),
                orientation=np.array([0, 0, 0])
            )
        )

        Camera_Config().add_camera(camera_l)


    def OpenCamera(self):
        if not self.zed.is_opened():
            self.init.camera_resolution = sl.RESOLUTION.HD1080
            self.init.camera_fps = 30
            self.init.depth_mode = sl.DEPTH_MODE.NONE
            if self.zed.open(self.init) != sl.ERROR_CODE.SUCCESS:
                print("Error: Camera Open Failed")
                return False

            return True
        return False
    
    def CloseCamera(self):
        self.zed.close()

    def get_frame(self, view):
        if not self.zed.is_opened():
            # print("Error: ZED is not opened")
            return None

        if self.zed.grab() == sl.ERROR_CODE.SUCCESS:

            if view == "left":
                if self.zed.retrieve_image(self.left_image, sl.VIEW.LEFT) == sl.ERROR_CODE.SUCCESS:
                    return cv2.cvtColor(self.left_image.get_data(), cv2.COLOR_RGBA2BGR)
                else:
                    print("Error: Failed to retrieve left image")
                    return None
            elif view == "right":
                if self.zed.retrieve_image(self.right_image, sl.VIEW.RIGHT) == sl.ERROR_CODE.SUCCESS:
                    return cv2.cvtColor(self.right_image.get_data(), cv2.COLOR_RGBA2BGR)
                else:
                    print("Error: Failed to retrieve right image")
                    return None
            else:
                print("Error: Invalid view specified")
                return None

        return None