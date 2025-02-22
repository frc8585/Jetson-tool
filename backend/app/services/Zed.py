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
            self.zed.set_camera_settings(sl.VIDEO_SETTINGS.WHITEBALANCE_TEMPERATURE, -1)
            self.zed.set_camera_settings(sl.VIDEO_SETTINGS.EXPOSURE, -1)  # 自動曝光
            self.zed.set_camera_settings(sl.VIDEO_SETTINGS.GAIN, -1)      # 自動增益

            return True
        return False
    
    def CloseCamera(self):
        self.zed.close()
        cv2.destroyAllWindows()

    def ImageProcessing(self):
        # 取得影像
        if self.zed.grab() == sl.ERROR_CODE.SUCCESS:
            self.zed.retrieve_image(self.left_image, sl.VIEW.LEFT)
            self.zed.retrieve_image(self.right_image, sl.VIEW.RIGHT)

            # 轉換成 BGR
            left_np = self.left_image.get_data()
            right_np = self.right_image.get_data()

            # 轉換成灰階 (加速特徵點匹配)
            left_gray = cv2.cvtColor(left_np, cv2.COLOR_RGBA2GRAY)
            right_gray = cv2.cvtColor(right_np, cv2.COLOR_RGBA2GRAY)

            # 辨識 AprilTag
            results = detector.detect(left_np, "zed_left")

            if results:
                for result in results:
                    # 繪製 Tag 邊界
                    for i in range(4):
                        pt1 = np.round(result.corner[i]).astype(int)
                        pt2 = np.round(result.corner[(i + 1) % 4]).astype(int)
                        cv2.line(left_np, tuple(pt1), tuple(pt2), (0, 255, 0), 2)

                    cv2.putText(left_np, f"ID: {result.id}", 
                                (int(result.corner[0][0]), int(result.corner[0][1]) - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

                    #繪製場地
                    if data_processor.get_latest_data().robot:
                        for field in self.field:
                            
                            if result.id in field["Tags"]:
                                for name,child in field["child"].items():
                                    match child["shape"]:
                                        case "rectangle":
                                            cv2.rectangle(left_np, (child["x"], child["y"]), (child["x"] + child["w"], child["y"] + child["h"]), (0, 255, 0), 2)
                                        case "circle":
                                            self.draw_circle(left_np, child["center"], child["r"], child["normal"], (0, 255, 0), 2)
                                        case _:
                                            print("Unknown shape")
                                break
            # 顯示影像
            cv2.imshow("final", left_np)
            cv2.waitKey(1)

    def draw_circle(self, frame, center, radius, normal_vector, color=(0, 255, 0), thickness=2):
        center = np.array(center).astype(np.float64)
        radius = np.float64(radius)
        normal_vector = np.array(normal_vector).astype(np.float64)
        rvec = data_processor.get_latest_data().robot.revc
        tvec = data_processor.get_latest_data().robot.tvec
        K = data_processor.K

        center_2, _ = cv2.projectPoints(center, rvec, tvec, K, distCoeffs=None)

        cv2.circle(frame, tuple(center_2.ravel().astype(int)), 10, color, thickness)
