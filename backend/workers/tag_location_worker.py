import queue
import threading
import time

import cv2
import numpy as np

from backend.models.buffer import SmartLifoBuffer
from backend.models.data import LocationData
from backend.services.camera_manager_service import CameraManager
from backend.services.field_manager_service import FieldManager

# TODO 驗證資料數值與校準
class TagLocationWorker(threading.Thread):
    def __init__(self, fast_buffer: SmartLifoBuffer, history_buffer: SmartLifoBuffer, camera_manager: CameraManager, field_manager: FieldManager):
        super().__init__()
        self.fast_buffer = fast_buffer
        self.history_buffer = history_buffer
        self.camera_manager = camera_manager
        self.field_manager = field_manager
        self.running = True

    def run(self):
        while self.running:
            recognition_result = self.fast_buffer.get_newest()
            if not recognition_result:
                recognition_result = self.history_buffer.get_newest()
            if not recognition_result:
                recognition_result = self.fast_buffer.get_newest(timeout=1)
            if not recognition_result:
                continue
        
            print(f"Processing recognition result from camera {recognition_result.camera_id} at {recognition_result.timestamp}")
        
            # 1. Get Camera Config
            camera_config = None
            for cam in self.camera_manager.cameras:
                if cam.camera_id == recognition_result.camera_id:
                    camera_config = cam.config
                    break
            
            if not camera_config:
                print(f"Camera config not found for {recognition_result.camera_id}")
                continue

            K = np.array(camera_config.K)
            D = np.array(camera_config.D) if camera_config.D else None

            datas = []
            
            for tag in recognition_result.tags:
                # 2. Get Tag World Corners
                object_points = self.field_manager.get_tag_corners(tag.tag_id)
                if object_points is None:
                    # print(f"Tag {tag.tag_id} not found in field config.")
                    continue

                # 3. Solve PnP
                # object_points: 3D points in world coordinate
                # tag.corners: 2D points in image plane
                success, rvec, tvec = cv2.solvePnP(object_points, tag.corners, K, D)
                
                if not success:
                    continue

                R_mat, _ = cv2.Rodrigues(rvec)

                # Camera position in world coordinate = -R^T * t
                camera_position = -np.dot(R_mat.T, tvec)

                # Calculate Euler angles (This part depends on rotation convention, assuming XYZ here for now)
                # Note: This orientation calculation might need adjustment based on specific requirements
                pitch = np.arcsin(R_mat[2][0])
                yaw = np.arctan2(R_mat[1][0], R_mat[0][0])
                roll = np.arctan2(R_mat[2][1], R_mat[2][2])
            
                datas.append(LocationData(position=camera_position.ravel(), orientation=(pitch, yaw, roll), timestamp=recognition_result.timestamp))
            
            if datas:
                avg_position = np.mean([d.position for d in datas], axis=0)
                avg_orientation = np.mean([d.orientation for d in datas], axis=0)
                
                print(f"Estimated Camera Position: {avg_position}, Orientation: {avg_orientation}")
            
    def stop(self):
        self.running = False