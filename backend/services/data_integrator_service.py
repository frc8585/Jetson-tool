"""
數據整合器 - 階段 1 版本
簡單加權平均融合多相機觀測
"""
from collections import deque
from threading import Lock
import time
import numpy as np
from backend.models.data import LocationData


class FusedState:
    """融合後的狀態"""
    def __init__(self):
        self.timestamp = None
        self.position = None
        self.yaw = None
        self.num_observations = 0
        

class DataIntegrator:
    """
    資料整合器 (階段 1: 簡單版本)
    
    功能:
    - 收集來自多個相機的觀測
    - 簡單加權平均融合
    - 維護最新融合狀態
    """
    
    def __init__(self, trajectory_logger=None):
        # 記憶體緩存
        self.latest_fused = None
        self.lock = Lock()
        
        # 觀測收集窗口（時間窗口 100ms）
        self.observation_window = deque(maxlen=100)
        self.window_duration = 0.1  # 100ms
        
        # 軌跡記錄器（可選）
        self.trajectory_logger = trajectory_logger
        
    def add_observation(self, location: LocationData):
        """
        接收單一觀測
        
        Args:
            location: 來自單一相機的位置觀測
        """
        # 立即記錄原始觀測到檔案
        if self.trajectory_logger:
            self.trajectory_logger.log_observation(location)
        
        with self.lock:
            self.observation_window.append(location)
            
            # 觸發融合（簡單策略：每次新觀測都融合）
            self._fuse_observations()
    
    def _fuse_observations(self):
        """
        簡單加權平均融合
        
        階段 1: 所有觀測權重相同
        """
        if not self.observation_window:
            return
        
        current_time = time.time()
        
        # 收集最近的觀測（100ms 內）
        recent_obs = [
            obs for obs in self.observation_window
            if current_time - obs.timestamp < self.window_duration
        ]
        
        if not recent_obs:
            return
        
        # 簡單平均（階段1：所有觀測權重相同）
        positions = np.array([obs.position for obs in recent_obs])
        yaws = np.array([obs.orientation[1] for obs in recent_obs])  # yaw is index 1
        
        avg_position = np.mean(positions, axis=0)
        avg_yaw = np.mean(yaws)
        
        # 更新融合狀態
        self.latest_fused = FusedState()
        self.latest_fused.timestamp = current_time
        self.latest_fused.position = avg_position
        self.latest_fused.yaw = avg_yaw
        self.latest_fused.num_observations = len(recent_obs)
    
    def get_latest(self):
        """
        獲取最新融合狀態
        
        Returns:
            FusedState 或 None
        """
        with self.lock:
            return self.latest_fused
