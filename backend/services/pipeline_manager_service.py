import queue
import threading

from backend.services.camera_manager_service import CameraManager
from backend.workers.recognition_worker import LocalizationWorker


class PipelineManager(threading.Thread):
    def __init__(self, camera_manager: CameraManager):
        super().__init__()
        self.camera_manager = camera_manager
        self._stop_event = threading.Event()

    def run(self):
        while not self._stop_event.is_set():
            try:
                recognition_result = self.camera_manager.recognition_results.get_nowait()
                print(f"Received recognition result from camera {recognition_result.camera_id} at {recognition_result.timestamp}, tags: {len(recognition_result.tags)}")
            except queue.Empty:
                pass
                
        
    def stop(self):
        self._stop_event.set()
        pass