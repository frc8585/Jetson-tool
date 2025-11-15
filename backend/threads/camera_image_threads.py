import threading, cv2, queue
import time

from backend.models import Camera

class CameraImageThread(threading.Thread):
    def __init__(self, cap: cv2.VideoCapture, buffers: queue.Queue):
        super().__init__()
        self.cap = cap
        self.buffers = buffers
        self.running = True

    def run(self):
        try:
            while self.running:
                ret, frame = self.cap.read()
                timestamp = time.time()
                if ret:
                    # 清空隊列中的舊幀
                    try: 
                        self.buffers.get_nowait()
                    except queue.Empty:
                        pass

                    # 將新的幀放入隊列
                    self.buffers.put_nowait((frame, timestamp))
        except Exception as e:
            print(f"Error in CameraImageThread: {e}")
        finally:
            self.cap.release()
            self.running = False

    
    def stop(self):
        self.running = False
        