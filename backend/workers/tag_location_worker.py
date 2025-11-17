import queue
import threading
import time

from backend.models.buffer import SmartLifoBuffer


class TagLocationWorker(threading.Thread):
    def __init__(self, fast_buffer: SmartLifoBuffer, history_buffer: SmartLifoBuffer):
        super().__init__()
        self.fast_buffer = fast_buffer
        self.history_buffer = history_buffer
        self.running = True

    def run(self):
        while self.running:
            recognition_result = self.fast_buffer.get_newest()
            if not recognition_result:
                recognition_result = self.history_buffer.get_newest()
            if not recognition_result:
                recognition_result = self.fast_buffer.get_newest(timeout=1)
                continue
            
            # 處理辨識結果
            print("Processing tag location:", recognition_result)
            
            
            
    def stop(self):
        self.running = False