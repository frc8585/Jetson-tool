from collections import deque
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
        
        
class SmartLifoBuffer:
    def __init__(self, maxsize: int, history_queue: 'SmartLifoBuffer' = None):
        """
        maxsize: 緩衝區最大容量
        history_queue: (選填) 如果有舊資料被擠出去，要丟去哪裡？
        """
        self.maxlen = maxsize
        self.buffer = deque() # 雙端佇列
        self.history_queue = history_queue
        self.lock = threading.Lock()
        self.not_empty = threading.Condition(self.lock)

    def put_newest(self, item):
        """
        Router 呼叫此方法放入新資料。
        邏輯：放入右邊 (最新)。如果滿了，把左邊 (最舊) 擠出去。
        """
        with self.lock:
            # 1. 檢查是否滿了
            if len(self.buffer) >= self.maxlen:
                # 2. 【關鍵】從左邊彈出最舊的 (FIFO Eviction)
                oldest_item = self.buffer.popleft()
                
                # 3. 如果有設定歷史區，把這個被犧牲的舊資料存起來
                if self.history_queue:
                    try:
                        self.history_queue.put_newest(oldest_item)
                    except:
                        pass # 歷史區也滿了，只能丟棄

            # 4. 把最新的放入右邊
            self.buffer.append(item)
            
            # 5. 通知等待中的 Worker
            self.not_empty.notify()

    def get_newest(self, timeout=0):
        """
        Worker 呼叫此方法拿資料。
        邏輯：從右邊拿 (LIFO Retrieval)。
        """
        with self.not_empty:
            # 如果空的回傳空值
            if not self.buffer:
                signaled = self.not_empty.wait(timeout=timeout)
                if not signaled:
                    return None # 超時了還是空的
            
            # 【關鍵】從右邊彈出最新的 (LIFO Retrieval)
            return self.buffer.pop()