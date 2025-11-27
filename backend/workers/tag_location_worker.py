import queue
import threading
import time

import cv2
import numpy as np

from backend.models.buffer import SmartLifoBuffer
from backend.models.data import LocationData

# TODO 驗證資料數值與校準
class TagLocationWorker(threading.Thread):
    def __init__(self, fast_buffer: SmartLifoBuffer, history_buffer: SmartLifoBuffer):
        super().__init__()
        self.fast_buffer = fast_buffer
        self.history_buffer = history_buffer
        self.running = True
        self.field = np.array([[0, 0, 0], [16.5, 0, 0], [16.5, -16.5, 0], [0, -16.5, 0]])  # TODO 加载实际场地数据
        self.K = np.array([[600, 0, 320], [0, 600, 240], [0, 0, 1]])  # TODO 使用实际相机内参

    def run(self):
        while self.running:
            recognition_result = self.fast_buffer.get_newest()
            if not recognition_result:
                recognition_result = self.history_buffer.get_newest()
            if not recognition_result:
                recognition_result = self.fast_buffer.get_newest(timeout=1)
            if not recognition_result:
                continue
        
            print(f"Processing recognition result from camera {recognition_result.camera_id} at {recognition_result.timestamp}")
        
            datas = []
            
            for tag in recognition_result.tags:
                _, rvec, tvec = cv2.solvePnP(self.field, tag.corners, self.K, None)
                R, _ = cv2.Rodrigues(rvec)

                camera_position = -np.dot(R.T, tvec)

                pitch = np.arcsin(R[2][0])
                yaw = np.arctan2(R[1][0], R[0][0])
                roll = np.arctan2(R[2][1], R[2][2])
            
                datas.append(LocationData(position=camera_position.ravel(), orientation=(pitch, yaw, roll), timestamp=recognition_result.timestamp))
            
            if datas:
                avg_position = np.mean([d.position for d in datas], axis=0)
                avg_orientation = np.mean([d.orientation for d in datas], axis=0)
                
                print(f"Estimated Camera Position: {avg_position}, Orientation: {avg_orientation}")
            
    def stop(self):
        self.running = False