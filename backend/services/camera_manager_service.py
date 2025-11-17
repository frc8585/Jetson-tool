import queue
import cv2
import yaml
import os
import threading

from backend.models import Camera
from backend.models import CameraImageBuffer
from backend.utils import camera as camera_utils
# 
from backend.workers.camera_image_worker import CameraImageWorker
from backend.workers.recognition_worker import LocalizationWorker 

# 
CAMERA_CONFIG_DIR = os.path.join("backend", "config", "camera.yml")

class CameraManager:
    """
    """
    # TODO 撰寫相機管理器的方法/類別註解
    # TODO 撰寫影像處理程式獲取影像的邏輯
    # TODO 整理程式碼

    def __init__(self, config_path=CAMERA_CONFIG_DIR):
        """
        """
        self.config_path = config_path
        
        # 1. 
        self.cameras = []          # 
        self.camera_cap = {}       # 
        self.camera_image = {}     # 
        self.camera_image_threads = {}   # 
        self.image_processing_threads = {}  #
        
        self.recognition_results = queue.Queue(maxsize=100) 
        
        # 2. 
        self.lock = threading.Lock()

    # --------------- 
    
    def start(self):
        """
        """
        print("Starting CameraManager...")
        if not os.path.exists(self.config_path):
            self._config_reset() # 
        
        self.load_camera_config()
        
        # 
        with self.lock:
            # 
            for cam in self.cameras:
                try:
                    self._start_camera_instance(cam)
                except Exception as e:
                    print(f"Error starting camera {cam.camera_id} on init: {e}")

    def stop_all(self):
        """
        """
        print("Stopping all camera threads...")
        with self.lock:
            # 
            # 
            camera_ids_to_stop = list(self.camera_image_threads.keys())
            
            for cam_id in camera_ids_to_stop:
                self._stop_camera_instance(cam_id)
        print("All cameras stopped.")

    # --------------- 
    
    def _start_camera_instance(self, cam: Camera):
        """
        """
        # 
        # 
        
        print(f"Attempting to start instance for {cam.camera_id}...")
        try:
            cap = camera_utils.start_camera_cap(cam)
            self.camera_cap[cam.camera_id] = cap

            # 影像緩衝區
            buffers = CameraImageBuffer()
            self.camera_image[cam.camera_id] = buffers
            
            # 啟動影像擷取執行緒
            thread = CameraImageWorker(cap, buffers)
            thread.name = f"CameraThread-{cam.camera_id}"
            thread.start()
            self.camera_image_threads[cam.camera_id] = thread
            
            # 啟動影像處理執行緒
            thread_loc = LocalizationWorker(cam.camera_id, buffers, self.recognition_results)
            thread_loc.name = f"LocalizationWorker-{cam.camera_id}"
            thread_loc.start()
            self.image_processing_threads[cam.camera_id] = thread_loc
            
            print(f"Successfully started instance for {cam.camera_id}")
            
        

        except Exception as e:
            print(f"Failed to start instance for {cam.camera_id}: {e}")
            # 
            if cam.camera_id in self.camera_cap:
                self.camera_cap.pop(cam.camera_id).release()
            raise # 

    def _stop_camera_instance(self, camera_id: str):
        """
        """
        # 
        print(f"Stopping instance for {camera_id}...")
        
        thread = self.camera_image_threads.pop(camera_id, None)
        if thread:
            thread.stop()
            thread.join() # 

        cap = self.camera_cap.pop(camera_id, None)
        if cap:
            cap.release()
            
        self.camera_image.pop(camera_id, None)
        print(f"Instance for {camera_id} stopped.")

    # --------------- 

    def add_camera(self, camera: Camera):
        """
        """
        with self.lock:
            if any(cam.camera_id == camera.camera_id for cam in self.cameras):
                raise ValueError(f"Camera with ID {camera.camera_id} already exists.")
            
            try:
                # 
                self._start_camera_instance(camera)
                
                # 
                self.cameras.append(camera)
                self.save_camera_config()
                
            except Exception as e:
                # 
                # 
                self._stop_camera_instance(camera.camera_id)
                raise ValueError(f"Failed to add and start camera {camera.camera_id}: {e}")

    def remove_camera(self, camera_id: str):
        """
        """
        with self.lock:
            # 1. 
            cam_to_remove = None
            for cam in self.cameras:
                if cam.camera_id == camera_id:
                    cam_to_remove = cam
                    break
            
            if cam_to_remove is None:
                raise ValueError(f"Camera with ID {camera_id} not found in config.")

            # 2. 
            self._stop_camera_instance(camera_id)
            
            # 3. 
            self.cameras.remove(cam_to_remove)
            self.save_camera_config()

    def get_camera_img(self, camera_id: str):
        """
        """
        buffers = None
        with self.lock:
            # 
            buffers = self.camera_image.get(camera_id)

        if buffers is None:
            # 
            raise ValueError(f"No image buffer found for camera ID {camera_id}")
            
        try:
            # 
            frame, timestamp = buffers.get_nowait()
            return frame, timestamp
        except queue.Empty:
            # 
            return None, None

    def get_camera_config(self):
        """
        """
        with self.lock:
            # 
            return self.cameras.copy()

    # --------------- 
    
    def _config_reset(self):
        """
        """
        print(f"Resetting config file at {self.config_path}")
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, "w") as f:
            yaml.safe_dump({"cameras": []}, f)

    def load_camera_config(self):
        """
        """
        print(f"Loading camera config from {self.config_path}...")
        try:
            with open(self.config_path, "r") as f:
                config = yaml.safe_load(f)
                
            if config is None:
                self._config_reset()
                return

            with self.lock:
                self.cameras = [] # 
                for cam_dict in config.get("cameras", []):
                    self.cameras.append(Camera(**cam_dict))
                    
        except Exception as e:
            print(f"Error loading camera config: {e}")

    def save_camera_config(self):
        """
        """
        # 
        # 
        
        try:
            if not os.path.exists(self.config_path):
                self._config_reset()
                
            with open(self.config_path, "w") as f:
                # 
                config = {"cameras": [cam.model_dump(mode='json') for cam in self.cameras]}
                yaml.safe_dump(config, f)
                
        except Exception as e:
            print(f"Error saving camera config: {e}")