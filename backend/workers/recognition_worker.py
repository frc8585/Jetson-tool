

import threading
import queue

class LocalizationWorker(threading.Thread):
    def __init__(self, image_queue: queue.Queue):
        super().__init__()
        self.image_queue = image_queue
        self.running = True

    def run(self):
        while self.running:
            # TODO 撰寫影像辨識邏輯
            
            if not self.image_queue.empty():
                print("test localization worker. size of queue:", self.image_queue.qsize())
                self.image_queue.get_nowait()
            else:
                print("localization worker: queue is empty")

    def stop(self):
        self.running = False