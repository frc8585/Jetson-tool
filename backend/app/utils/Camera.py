import wmi
import cv2
import numpy as np
import time
import pythoncom

from pygrabber.dshow_graph import FilterGraph

from app.models.Camera import Camera, Config
from config import Camera_Config

class Camera_tool:

    def get_all_camera(self):
        pythoncom.CoInitialize()
        w = wmi.WMI()
        graph = FilterGraph()

        devices = graph.get_input_devices()  # 獲取所有可用相機名稱
        camera_info = []
        for index, name in enumerate(devices):
            query = "SELECT * FROM Win32_PnPEntity WHERE Name LIKE '%{}%'".format(name)
            cameraid = w.query(query)
            camera_id = cameraid[0].DeviceID if cameraid else None

            camera_info.append(Camera(
                index = index,
                name = name,
                id = camera_id,
                config = None
            ))

            # 獲取相機設定
            camera_config = Camera_Config()
            config = camera_config.get_camera_by_id(camera_id)
            if config:
                config = config["config"]
            if config:
                camera_info[-1].config = Config(
                    K = np.array(config["K"]),
                    postion = np.array(config["postion"]),
                    orientation = np.array(config["orientation"]),
                    isenable = config["isenable"]
                )

        graph.stop()

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
    
    # 相機標定

def calibrate(camera_index, checker_row, checker_col, square_size, num_images=20, capture_interval=2):
    """
    相機標定函式
    
    Parameters:
    camera_index (int): 相機索引
    checker_row (int): 棋盤格行數
    checker_col (int): 棋盤格列數
    square_size (float): 棋盤格方格尺寸(公分)
    num_images (int): 要捕捉的圖片數量
    capture_interval (float): 捕捉圖片的時間間隔(秒)
    
    Returns:
    tuple: (camera_matrix, dist_coeffs, mean_error) 若成功
           (None, None, None) 若失敗
    """
    # 準備校正板的三維點
    objp = np.zeros((checker_row * checker_col, 3), np.float32)
    objp[:, :2] = np.mgrid[0:checker_row, 0:checker_col].T.reshape(-1, 2) * square_size

    # 儲存所有圖片的三維點和二維點
    object_points = []
    image_points = []
    image_size = None

    # 開啟相機
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print("無法打開攝影機！")
        return None, None, None

    captured_count = 0
    last_capture_time = time.time()

    # 捕捉圖片
    while captured_count < num_images:
        ret, frame = cap.read()
        if not ret:
            print("無法從攝影機讀取影像！")
            break

        if image_size is None:
            image_size = (frame.shape[1], frame.shape[0])

        current_time = time.time()
        if current_time - last_capture_time < capture_interval:
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        ret, corners = cv2.findChessboardCorners(gray, (checker_row, checker_col), None)

        if ret:
            object_points.append(objp)
            image_points.append(corners)

            cv2.drawChessboardCorners(frame, (checker_row, checker_col), corners, ret)
            captured_count += 1
            last_capture_time = current_time
            print(f"捕捉到第 {captured_count}/{num_images} 張影像")

        cv2.imshow('Calibration', frame)
        key = cv2.waitKey(1)
        if key == 27:  # ESC鍵退出
            break

    cap.release()
    cv2.destroyAllWindows()

    if captured_count < num_images:
        print("未捕捉到足夠的影像進行標定")
        return None, None, None

    # 進行相機標定
    ret, camera_matrix, dist_coeffs, rvecs, tvecs = cv2.calibrateCamera(
        object_points, image_points, image_size, None, None
    )

    if not ret:
        print("標定失敗！")
        return None, None, None

    # 計算重投影誤差
    total_error = 0
    total_points = 0
    for i in range(len(object_points)):
        imgpoints2, _ = cv2.projectPoints(
            object_points[i], rvecs[i], tvecs[i], camera_matrix, dist_coeffs
        )
        error = cv2.norm(image_points[i], imgpoints2, cv2.NORM_L2)
        total_error += error ** 2
        total_points += len(object_points[i])

    mean_error = np.sqrt(total_error / total_points)

    # 輸出結果
    print("標定成功！")
    print(f"相機矩陣：\n{camera_matrix}")
    print(f"畸變係數：\n{dist_coeffs}")
    print(f"平均重投影誤差: {mean_error} 像素")

    return camera_matrix, dist_coeffs, mean_error
