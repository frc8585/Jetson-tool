import cv2
import numpy as np
import pyzed.sl as sl

from app.services import detector, data_processor

class Zed:
    def __init__(self):
        self.zed = sl.Camera()
        self.init = sl.InitParameters()
        self.left_image = sl.Mat()
        self.right_image = sl.Mat()
        self.siftDetector = cv2.xfeatures2d.SIFT_create()

    def OpenCamera(self):
        if not self.zed.is_opened():
            self.init.camera_resolution = sl.RESOLUTION.HD720
            self.init.camera_fps = 60
            self.init.depth_mode = sl.DEPTH_MODE.NONE
            if self.zed.open(self.init) != sl.ERROR_CODE.SUCCESS:
                print("Error: Camera Open Failed")
                return False
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
            left_np = cv2.cvtColor(self.left_image.get_data(), cv2.COLOR_RGBA2BGR)
            right_np = cv2.cvtColor(self.right_image.get_data(), cv2.COLOR_RGBA2BGR)

            # 轉換成灰階 (加速特徵點匹配)
            left_gray = cv2.cvtColor(left_np, cv2.COLOR_BGR2GRAY)
            right_gray = cv2.cvtColor(right_np, cv2.COLOR_BGR2GRAY)



            
            # 辨識 AprilTag
            results = detector.detect(left_np, None)

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

            # 顯示影像
            cv2.imshow("final", left_np)
            cv2.waitKey(1)
