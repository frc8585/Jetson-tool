

import threading
import queue, cv2

from pupil_apriltags import Detector

from backend.models.camera import CameraImageBuffer

class LocalizationWorker(threading.Thread):
    def __init__(self, buffer: CameraImageBuffer):
        super().__init__()
        self.buffer = buffer
        self.running = True
        self.last_frame_id = -1
        
        self.detector = Detector(families="tag36h11")

    def run(self):
        while self.running:
            # TODO 撰寫影像辨識邏輯
            
            fram, timestamp, self.last_frame_id = self.buffer.wait_for_new_frame(self.last_frame_id)
            # TODO 處理取得的影像
            gray = cv2.cvtColor(fram, cv2.COLOR_BGR2GRAY)
            
            results = self.detector.detect(gray)
            for r in results:
                print(f"Detected tag id: {r.tag_id} at center: {r.center}")
            
            # print(f"Processed frame id: {self.last_frame_id}")

    def stop(self):
        self.running = False