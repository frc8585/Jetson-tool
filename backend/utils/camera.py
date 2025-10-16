import pyudev
import cv2

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
    pass
