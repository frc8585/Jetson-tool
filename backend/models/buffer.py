import threading


class CameraImageBuffer:
    """
    """

    def __init__(self):
        # 1. 
        self.condition = threading.Condition()
        
        # 2. 
        self.latest_frame = None
        self.timestamp = 0
        self.frame_id = -1
        
    def set(self, frame, timestamp):
        with self.condition:
            self.latest_frame = frame
            self.timestamp = timestamp
            self.frame_id += 1
            self.condition.notify_all()
            
    def wait_for_new_frame(self, last_seen_id: int):
        """
        """
        with self.condition:
            # 
            # 
            while self.frame_id == last_seen_id:
                # 
                self.condition.wait() 
            
            # 
            return self.latest_frame, self.timestamp, self.frame_id
    
    def get_nowait(self):
        """
        """
        with self.condition:
            return self.latest_frame, self.timestamp