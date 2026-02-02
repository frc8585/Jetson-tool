"""
軌跡記錄器
非同步寫入 CSV 格式的原始觀測資料
"""
import queue
import threading
import time
from pathlib import Path
from datetime import datetime
from backend.models.data import LocationData


class TrajectoryLogger:
    """
    CSV 軌跡記錄器
    
    功能:
    - 非同步寫入 CSV 檔案
    - 記錄所有原始觀測
    - Session 管理
    """
    
    def __init__(self, output_dir="data/trajectories"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 寫入佇列（非同步）
        self.write_queue = queue.Queue(maxsize=10000)
        
        # 當前檔案
        self.current_file = None
        self.session_id = self._generate_session_id()
        
        # 背景寫入執行緒
        self.writer_thread = None
        self.running = False
    
    def start(self):
        """啟動記錄器"""
        self.running = True
        self._open_file()
        
        # 啟動寫入執行緒
        self.writer_thread = threading.Thread(target=self._write_loop, daemon=True)
        self.writer_thread.start()
        print(f"TrajectoryLogger started: {self.session_id}")
    
    def log_observation(self, location: LocationData):
        """
        記錄觀測（非阻塞）
        
        Args:
            location: 位置觀測資料
        """
        try:
            self.write_queue.put_nowait(location)
        except queue.Full:
            # 佇列滿，丟棄最舊的
            try:
                self.write_queue.get_nowait()
                self.write_queue.put_nowait(location)
            except:
                pass
    
    def _write_loop(self):
        """背景寫入循環"""
        while self.running:
            try:
                location = self.write_queue.get(timeout=1.0)
                self._write_to_csv(location)
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error writing to CSV: {e}")
    
    def _write_to_csv(self, location: LocationData):
        """寫入 CSV"""
        if not self.current_file:
            return
        
        # CSV 格式: timestamp,camera_id,x,y,z,yaw,error,tag_ids,num_tags
        tag_ids_str = ';'.join(map(str, location.tag_ids))
        error_val = location.error if location.error is not None else 0.0
        
        line = (
            f"{location.timestamp:.3f},"
            f"{location.camera_id},"
            f"{location.position[0]:.6f},{location.position[1]:.6f},{location.position[2]:.6f},"
            f"{location.orientation[1]:.6f},"  # yaw
            f"{error_val:.6f},"
            f"{tag_ids_str},"
            f"{location.num_tags}\n"
        )
        
        self.current_file.write(line)
        self.current_file.flush()
    
    def _open_file(self):
        """開啟新檔案"""
        filename = f"observations_{self.session_id}.csv"
        filepath = self.output_dir / filename
        
        self.current_file = open(filepath, 'w')
        
        # 寫入標頭
        header = "timestamp,camera_id,x,y,z,yaw,error,tag_ids,num_tags\n"
        self.current_file.write(header)
        self.current_file.flush()
        
        print(f"CSV file created: {filepath}")
    
    def _generate_session_id(self):
        """生成 Session ID"""
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def stop(self):
        """停止記錄器"""
        print("Stopping TrajectoryLogger...")
        self.running = False
        if self.writer_thread:
            self.writer_thread.join(timeout=5.0)
        if self.current_file:
            self.current_file.close()
        print("TrajectoryLogger stopped.")
