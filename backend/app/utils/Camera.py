import wmi

from pygrabber.dshow_graph import FilterGraph

from app.models.Camera import Camera

class Camera_tool:

    def get_all_camera(self):
        w = wmi.WMI()
        graph = FilterGraph()

        devices = graph.get_input_devices()  # 獲取所有可用相機名稱
        camera_info = []
        for index, name in enumerate(devices):
            query = "SELECT * FROM Win32_PnPEntity WHERE Name LIKE '%{}%'".format(name)
            cameraid = w.query(query)
            camera_info.append(Camera(
                index = index,
                name = name,
                id = cameraid[0].DeviceID if cameraid else None,
            ))

        graph.stop()

        return camera_info
    
    def get_camera_by_id(self, id):
        cameras = self.get_all_camera()
        for camera in cameras:
            print(camera.id)
            if camera.id == id:
                return camera
        return None

    def dict_to_camera(self, dict):
        return Camera(dict["index"], dict["name"], dict["id"], dict["config"] if "config" in dict else None)
