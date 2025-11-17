import queue
import threading

from backend.services.camera_manager_service import CameraManager
from backend.workers.recognition_worker import LocalizationWorker


class PipelineManager(threading.Thread):
    def __init__(self, camera_manager: CameraManager):
        super().__init__()
        self._stop_event = threading.Event()

    def run(self):
        pass
                
        
    def stop(self):
        self._stop_event.set()
        pass