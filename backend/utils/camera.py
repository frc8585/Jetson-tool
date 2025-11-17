import pyudev
import cv2
import time

from backend.models.camera import BackendType, Camera


def get_all_connected_cameras():
    """
    獲取所有目前設備連接的相機
    """
    # FIXME: 解決單向機占兩個位置會被當作兩個相機的問題
    cameras = []
    if pyudev is None:
        return cameras
    context = pyudev.Context()
    for device in context.list_devices(subsystem='video4linux'):
        cam = Camera(
            name=device.properties.get('ID_V4L_PRODUCT', device.sys_name),
            camera_id=device.device_node,  # OpenCV ID
            path=device.device_node,
            backend=BackendType.LINUX_UDEV,
        )
        cameras.append(cam)

    return cameras


def start_camera_cap(camera: Camera):
    backend_type = camera.backend
    if backend_type == BackendType.LINUX_UDEV:  # Linux UDEV backend
        cap = cv2.VideoCapture(camera.camera_id)
        if not cap.isOpened():
            raise ValueError(f"Cannot open camera at {camera.camera_id}")
        return cap
            
    elif backend_type == BackendType.OTHER:  # Other backend
        # TODO: 撰寫 其他後端的相機資訊取得程式碼
        pass

    else:
        raise ValueError("Unsupported backend type")
    
def get_camera_img(camera: Camera):
    cap = start_camera_cap(camera)
    if cap is None:
        raise ValueError(f"Could not get capture object for camera {camera.camera_id}")

    ret, frame = cap.read()
    timestamp = time.time()
    cap.release()

    if not ret:
        raise ValueError("Failed to capture image")
    
    return frame, timestamp


def get_frame_from_cap(cap:cv2.VideoCapture):
    """
    從 cv2.VideoCapture 物件中獲取一幀影像
    """
    ret, frame = cap.read()
    if not ret:
        raise ValueError("Failed to capture image from camera")
    return frame, time.time()

def detector_results_to_tagdata(results) -> list:
    from backend.models.camera import CameraTagData
    tag_data_list = []
    for r in results:
        tag_data = CameraTagData(
            tag_id=r.tag_id,
            center=(r.center[0], r.center[1]),
            corners=[(corner[0], corner[1]) for corner in r.corners]
        )
        tag_data_list.append(tag_data)
    return tag_data_list