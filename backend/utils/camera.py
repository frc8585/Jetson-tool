import pyudev
import cv2

from backend.models.camera import BackendType, Camera


def get_connected_cameras():
    cameras = []
    if pyudev is None:
        return cameras
    context = pyudev.Context()
    for device in context.list_devices(subsystem='video4linux'):
        cam = Camera(
            name=device.sys_name,
            camera_id=device.device_node,  # OpenCV uses device node (e.g., '/dev/video0')
            path=device.device_node,
            backend=BackendType.LINUX_UDEV,
        )
        cameras.append(cam)

    return cameras


def start_camera_cap(camera: Camera):
    backend_type = camera.backend
    if backend_type == BackendType.LINUX_UDEV:  # Linux UDEV backend
        # TODO: 撰寫 UDEV 取得相機資訊的程式碼
        pass
            
    elif backend_type == BackendType.OTHER:  # Other backend
        # TODO: 撰寫 其他後端的相機資訊取得程式碼
        pass

    else:
        raise ValueError("Unsupported backend type")
    
def get_camera_img(camera: Camera):
    pass