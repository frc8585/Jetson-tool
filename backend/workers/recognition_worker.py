

import threading
import queue

from backend.models.camera import CameraImageBuffer

class LocalizationWorker(threading.Thread):
    def __init__(self, buffer: CameraImageBuffer):
        super().__init__()
        self.buffer = buffer
        self.running = True
        self.last_frame_id = -1

    def run(self):
        while self.running:
            # TODO 撰寫影像辨識邏輯
            
            self.buffer.wait_for_new_frame(self.last_frame_id)
            # TODO 處理取得的影像
            # 更新 last_frame_id
            self.last_frame_id += 1
            print(f"Processed frame id: {self.last_frame_id}")

    def stop(self):
        self.running = False