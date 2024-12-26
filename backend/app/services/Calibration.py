import cv2
import numpy as np
import time

class CameraCalibrator:
    def __init__(self, checkerboard_size=(6, 4), square_size=3.3, camera_index=0, capture_interval=2):
        self.checkerboard_size = checkerboard_size
        self.square_size = square_size
        self.camera_index = camera_index
        self.capture_interval = capture_interval

        self.objp = np.zeros((checkerboard_size[0] * checkerboard_size[1], 3), np.float32)
        self.objp[:, :2] = np.mgrid[0:checkerboard_size[0], 0:checkerboard_size[1]].T.reshape(-1, 2) * square_size

        self.object_points = []
        self.image_points = []
        self.image_size = None

    def capture_images(self, num_images=10):
        cap = cv2.VideoCapture(self.camera_index)

        if not cap.isOpened():
            print("無法打開攝影機！")
            return False

        captured_count = 0
        last_capture_time = time.time()

        while captured_count < num_images:
            ret, frame = cap.read()
            if not ret:
                print("無法從攝影機讀取影像！")
                break

            if self.image_size is None:
                self.image_size = (frame.shape[1], frame.shape[0])

            current_time = time.time()
            if current_time - last_capture_time < self.capture_interval:
                continue

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            ret, corners = cv2.findChessboardCorners(gray, self.checkerboard_size, None)

            if ret:
                self.object_points.append(self.objp)
                self.image_points.append(corners)

                cv2.drawChessboardCorners(frame, self.checkerboard_size, corners, ret)
                captured_count += 1
                last_capture_time = current_time
                print(f"捕捉到第 {captured_count}/{num_images} 張影像")

            cv2.imshow('Calibration', frame)
            key = cv2.waitKey(1)
            if key == 27:
                break

        cap.release()
        cv2.destroyAllWindows()

        if captured_count < num_images:
            print("未捕捉到足夠的影像進行標定")
            return False

        return True

    def calibrate_camera(self):
        if self.image_size is None:
            print("無法標定，未檢測到影像尺寸！")
            return None, None, None, None, None

        ret, camera_matrix, dist_coeffs, rvecs, tvecs = cv2.calibrateCamera(
            self.object_points, self.image_points, self.image_size, None, None
        )

        if not ret:
            print("標定失敗！")
            return None, None, None, None, None

        fx = camera_matrix[0, 0]
        fy = camera_matrix[1, 1]
        cx = camera_matrix[0, 2]
        cy = camera_matrix[1, 2]

        print("標定成功！")
        print(f"fx: {fx}, fy: {fy}, cx: {cx}, cy: {cy}")

        return camera_matrix, dist_coeffs, rvecs, tvecs

    def compute_reprojection_error(self, camera_matrix, dist_coeffs, rvecs, tvecs):
        total_error = 0
        total_points = 0

        for i in range(len(self.object_points)):
            imgpoints2, _ = cv2.projectPoints(
                self.object_points[i], rvecs[i], tvecs[i], camera_matrix, dist_coeffs
            )
            error = cv2.norm(self.image_points[i], imgpoints2, cv2.NORM_L2)
            total_error += error ** 2
            total_points += len(self.object_points[i])

        mean_error = np.sqrt(total_error / total_points)
        print(f"平均重投影誤差: {mean_error} 像素")
        return mean_error

    def run_calibration(self, num_images=10):
        print("=== 開始攝影機標定 ===")

        if not self.capture_images(num_images):
            print("捕捉影像失敗，無法進行標定")
            return

        camera_matrix, dist_coeffs, rvecs, tvecs = self.calibrate_camera()

        if camera_matrix is not None:
            self.compute_reprojection_error(camera_matrix, dist_coeffs, rvecs, tvecs)

if __name__ == "__main__":
    calibrator = CameraCalibrator(checkerboard_size=(4, 6), square_size=3.22, camera_index=0, capture_interval=2)
    calibrator.run_calibration(num_images=20)
