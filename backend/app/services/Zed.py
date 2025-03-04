import cv2
import numpy as np
import pyzed.sl as sl

from app.services import detector, data_processor
from config import Field

class Zed:
    def __init__(self):
        self.zed = sl.Camera()
        self.init = sl.InitParameters()
        self.left_image = sl.Mat()
        self.right_image = sl.Mat()
        self.field = np.array(Field().get_field_by_key('2025').get("Field"))

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
        cv2.destroyAllWindows()

    def get_frame(self, view):
        if not self.zed.is_opened():
            print("Error: Camera is not opened")
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