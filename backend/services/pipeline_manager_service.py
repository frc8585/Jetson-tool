import queue
import threading

from backend.models.buffer import SmartLifoBuffer
from backend.services.camera_manager_service import CameraManager
from backend.services.field_manager_service import FieldManager
from backend.workers.recognition_worker import RecognitionWorker
from backend.workers.tag_location_worker import TagLocationWorker


class PipelineManager(threading.Thread):
    def __init__(self, camera_manager: CameraManager, field_manager: FieldManager, localization_workers_size=1):
        super().__init__()
        self.localization_workers_size = localization_workers_size
        self.camera_manager = camera_manager
        self.field_manager = field_manager
        self._stop_event = threading.Event()
        
        # ----- 工作者列表 -----
        self.tag_location_workers = []
        self.history_buffer = SmartLifoBuffer(maxsize=100)
        self.fast_buffer = SmartLifoBuffer(maxsize=localization_workers_size, history_queue=self.history_buffer)

    def run(self):
        # ========== 初始化 ==========
        # ----- 啟動工作者 -----
        for _ in range(self.localization_workers_size):
            thread = TagLocationWorker(self.fast_buffer, self.history_buffer, self.camera_manager, self.field_manager)
            thread.start()
            self.tag_location_workers.append(thread)
        
        # ========== 主迴圈 ==========
        while not self._stop_event.is_set():
            try:
                recognition_result = self.camera_manager.recognition_results.get(timeout=1)
                
                self.fast_buffer.put_newest(recognition_result)
            except queue.Empty:
                continue
        
    def stop(self):
        self._stop_event.set()
        pass