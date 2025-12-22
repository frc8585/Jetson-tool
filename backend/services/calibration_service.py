import cv2
import numpy as np
import threading
import logging
from enum import Enum, auto
from typing import Tuple, List, Optional, Dict, Any

from backend.services.camera_manager_service import CameraManager

logger = logging.getLogger(__name__)

class CalibrationState(Enum):
    IDLE = auto()
    READY_TO_CAPTURE = auto()
    PROCESSING = auto()

class CalibrationService:
    def __init__(self, camera_manager: CameraManager):
        self.camera_manager = camera_manager
        self._lock = threading.Lock()
        self._state = CalibrationState.IDLE
        
        # Session data
        self._active_camera_id: Optional[str] = None
        self._board_size: Tuple[int, int] = (9, 6)
        self._square_size: float = 0.025
        
        # Storage
        self._objpoints: List[np.ndarray] = [] # 3d point in real world space
        self._imgpoints: List[np.ndarray] = [] # 2d points in image plane.
        self._image_size: Optional[Tuple[int, int]] = None
        
        # Pre-calculated object points for the current board
        self._objp: Optional[np.ndarray] = None

    @property
    def state(self) -> CalibrationState:
        with self._lock:
            return self._state

    def start_session(self, camera_id: str, board_size: Tuple[int, int] = (9, 6), square_size: float = 0.025):
        """Initializes a calibration session."""
        with self._lock:
            if self._state != CalibrationState.IDLE:
                raise RuntimeError(f"Calibration session already active (State: {self._state.name})")
            
            self._active_camera_id = camera_id
            self._board_size = board_size
            self._square_size = square_size
            
            # Reset storage
            self._objpoints = []
            self._imgpoints = []
            self._image_size = None
            
            # Prepare object points
            # (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
            self._objp = np.zeros((board_size[0] * board_size[1], 3), np.float32)
            self._objp[:, :2] = np.mgrid[0:board_size[0], 0:board_size[1]].T.reshape(-1, 2)
            self._objp *= square_size
            
            self._state = CalibrationState.READY_TO_CAPTURE
            logger.info(f"Started calibration session for camera {camera_id}")

    def add_sample(self, camera_id: str) -> Tuple[bool, int]:
        """
        Captures a frame, detects corners, and stores them if found.
        Returns (success, corner_count).
        """
        # 1. Validate state and camera_id
        with self._lock:
            if self._state != CalibrationState.READY_TO_CAPTURE:
                raise RuntimeError(f"Cannot add sample in state {self._state.name}")
            if camera_id != self._active_camera_id:
                raise ValueError(f"Session is active for camera {self._active_camera_id}, not {camera_id}")
            
            current_board_size = self._board_size
            current_objp = self._objp

        # 2. Get image (outside lock to avoid blocking)
        try:
            frame, _ = self.camera_manager.get_camera_img(camera_id)
        except Exception as e:
            logger.error(f"Failed to get image from camera {camera_id}: {e}")
            return False, 0

        if frame is None:
            return False, 0

        # 3. Process image
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Store image size if not set
        with self._lock:
            if self._image_size is None:
                self._image_size = gray.shape[::-1] # (width, height)
            elif self._image_size != gray.shape[::-1]:
                logger.warning("Image size changed during calibration session. Ignoring sample.")
                return False, 0

        # Find corners
        ret, corners = cv2.findChessboardCorners(gray, current_board_size, None)

        if ret:
            # Refine corners
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
            corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)

            # Store points
            with self._lock:
                # Double check state hasn't changed
                if self._state != CalibrationState.READY_TO_CAPTURE:
                    return False, 0
                
                self._objpoints.append(current_objp)
                self._imgpoints.append(corners2)
                count = len(self._imgpoints)
            
            logger.info(f"Added sample {count} for camera {camera_id}")
            return True, count
        
        return False, 0

    def compute_calibration(self, camera_id: str) -> Dict[str, Any]:
        """
        Computes calibration parameters.
        Returns dictionary with K, D, and reprojection error.
        """
        with self._lock:
            if self._state != CalibrationState.READY_TO_CAPTURE:
                raise RuntimeError(f"Cannot compute calibration in state {self._state.name}")
            if camera_id != self._active_camera_id:
                raise ValueError(f"Session is active for camera {self._active_camera_id}, not {camera_id}")
            
            if len(self._objpoints) < 1: # Need at least some points. Usually > 10 is recommended.
                raise ValueError("Not enough samples to calibrate")

            self._state = CalibrationState.PROCESSING
            objpoints = list(self._objpoints)
            imgpoints = list(self._imgpoints)
            image_size = self._image_size

        try:
            logger.info(f"Computing calibration for {camera_id} with {len(objpoints)} samples...")
            ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(
                objpoints, imgpoints, image_size, None, None
            )

            # Calculate reprojection error
            mean_error = 0
            for i in range(len(objpoints)):
                imgpoints2, _ = cv2.projectPoints(objpoints[i], rvecs[i], tvecs[i], mtx, dist)
                error = cv2.norm(imgpoints[i], imgpoints2, cv2.NORM_L2) / len(imgpoints2)
                mean_error += error
            total_error = mean_error / len(objpoints)

            result = {
                "K": mtx.tolist(),
                "D": dist.ravel().tolist(),
                "reprojection_error": total_error,
                "image_count": len(objpoints),
                "image_size": image_size
            }
            
            logger.info(f"Calibration successful. Error: {total_error}")
            return result

        except Exception as e:
            logger.error(f"Calibration failed: {e}")
            raise e
        finally:
            # Reset state to IDLE after computation
            with self._lock:
                self._state = CalibrationState.IDLE
                self._active_camera_id = None
                self._objpoints = []
                self._imgpoints = []
                self._image_size = None
                self._objp = None

    def cancel_session(self):
        """Cancels the current session and clears state."""
        with self._lock:
            self._state = CalibrationState.IDLE
            self._active_camera_id = None
            self._objpoints = []
            self._imgpoints = []
            self._image_size = None
            self._objp = None
            logger.info("Calibration session cancelled")

    def get_session_info(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "state": self._state.name,
                "active_camera_id": self._active_camera_id,
                "sample_count": len(self._imgpoints)
            }
