import threading, cv2, queue
import time

from backend.models import Camera

class CameraImageWorker(threading.Thread):
    def __init__(self, cap: cv2.VideoCapture, condition: threading.Condition):
        super().__init__()
        self.cap = cap
        self.condition = condition
        self.running = True

    def run(self):
        try:
            while self.running:
                ret, frame = self.cap.read()
                timestamp = time.time()
                if ret:
                    self.condition.set(frame, timestamp)
        except Exception as e:
            print(f"Error in CameraImageThread: {e}")
        finally:
            self.cap.release()
            self.running = False

    
    def stop(self):
        self.running = False
        