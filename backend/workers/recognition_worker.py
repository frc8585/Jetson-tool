

import threading
import queue, cv2

import numpy as np
from pupil_apriltags import Detector

from backend.models.camera import CameraImageBuffer, RecognitionResult
from backend.utils.camera import detector_results_to_tagdata

class LocalizationWorker(threading.Thread):
    def __init__(self, camera_id: str, image_buffer: CameraImageBuffer, results_queue: queue.Queue):
        super().__init__()
        self.camera_id = camera_id
        self.buffer = image_buffer
        self.results_queue = results_queue
        self.running = True
        self.last_frame_id = -1
        
        self.detector = Detector(families="tag36h11")

    def run(self):
        while self.running:            
            fram, timestamp, self.last_frame_id = self.buffer.wait_for_new_frame(self.last_frame_id)
            
            gray = cv2.cvtColor(fram, cv2.COLOR_BGR2GRAY)
            
            results = self.detector.detect(gray)
            
            if not results:
                continue
            
            data = detector_results_to_tagdata(results)
            
            recognition_result = RecognitionResult(
                camera_id=self.camera_id,
                timestamp=timestamp,
                tags=data
            )
            
            if self.results_queue.full():
                try:
                    self.results_queue.get_nowait()  # 移除最舊的項目
                except queue.Empty:
                    pass  # 如果隊列已經是空的，則忽略
            self.results_queue.put(recognition_result)

    def stop(self):
        self.running = False