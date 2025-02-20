import cv2
import numpy as np
import pyzed.sl as sl

class Zed:
    def __init__(self):
        self.zed = sl.Camera()
        self.init = sl.InitParameters()
        self.left_image = sl.Mat()
        self.right_image = sl.Mat()

    # 開啟相機
    def OpenCamera(self):
        if not self.zed.is_opened():
            self.init.camera_resolution = sl.RESOLUTION.HD720
            self.init.camera_fps = 30
            self.init.depth_mode = sl.DEPTH_MODE.NONE
            if self.zed.open(self.init) != sl.ERROR_CODE.SUCCESS:
                print("Error: Camera Open Failed")
                return False
            return True
        return False
    
    def CloseCamera(self):
        self.zed.close()

    def ImageProcessing(self):
        # Image processing
        # Grab an image
        if self.zed.grab() == sl.ERROR_CODE.SUCCESS: # A new image is available if grab() returns SUCCESS
            # Get the rectified left image
            self.zed.retrieve_image(self.left_image, sl.VIEW.LEFT)
            left_np = self.left_image.get_data()

            # Get the rectified right image
            self.zed.retrieve_image(self.right_image, sl.VIEW.RIGHT)
            right_np = self.right_image.get_data()


            # Display the images

            cv2.imshow("ZED left", left_np)
            cv2.imshow("ZED right", right_np)

            cv2.waitKey(1)