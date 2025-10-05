
import platform
import cv2

from backend.models.camera import BackendType, Camera

# Determine system type locally instead of relying on an external global.
system_type = platform.system()

# Ensure these names exist regardless of platform to avoid NameError
FilterGraph = None
pyudev = None

if system_type == "Windows":
    try:
        from pygrabber.dshow_graph import FilterGraph
    except ImportError:
        FilterGraph = None
elif system_type == "Linux":
    try:
        import pyudev # type: ignore
    except ImportError:
        pyudev = None

def get_connected_cameras():
    cameras = []
    if system_type == "Windows":
        graph = FilterGraph()
        devices = graph.get_input_devices()
        for idx, name in enumerate(devices):
            cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
            if cap.isOpened():
                cam = Camera(
                    name=name,
                    camera_id=idx,       # OpenCV index
                    path=name,           # 用 Friendly Name 做 path
                    backend=BackendType.WINDOWS_DSHOW,
                )
                cameras.append(cam)
                cap.release()
    elif system_type == "Linux":
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
    else:
        # TODO: 支援其他系統
        pass
    return cameras

def start_camera_cap(camera: Camera):
    backend_type = camera.backend
    if backend_type == BackendType.LINUX_UDEV:  # Linux UDEV backend
        if system_type != "Linux":
            raise EnvironmentError("LINUX_UDEV backend is only supported on Linux")
        
        # TODO: 撰寫 UDEV 取得相機資訊的程式碼
        pass
    
    elif backend_type == BackendType.WINDOWS_DSHOW:  # Windows DSHOW backend
        if system_type != "Windows":
            raise EnvironmentError("WINDOWS_DSHOW backend is only supported on Windows")

        # camera.camera_id is expected to be an integer index for DSHOW
        try:
            idx = int(camera.camera_id)
        except Exception:
            raise ValueError("camera_id must be an integer for WINDOWS_DSHOW backend")

        cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
        if not cap.isOpened():
            raise EnvironmentError(f"Failed to open camera index {idx} using DSHOW")
        return cap
            
    elif backend_type == BackendType.OTHER:  # Other backend
        # TODO: 撰寫 其他後端的相機資訊取得程式碼
        pass

    else:
        raise ValueError("Unsupported backend type")