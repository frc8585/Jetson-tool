import wmi

from pygrabber.dshow_graph import FilterGraph

class Camera:

    def get_all_camera(self):
        w = wmi.WMI()
        graph = FilterGraph()

        devices = graph.get_input_devices()  # 獲取所有可用相機名稱
        camera_info = []
        for index, name in enumerate(devices):
            query = "SELECT * FROM Win32_PnPEntity WHERE Name LIKE '%{}%'".format(name)
            cameraid = w.query(query)
            camera_info.append({
                "index": index,
                "name": name,
                "id": cameraid[0].DeviceID if cameraid else None,
            })

        graph.stop()

        return camera_info


