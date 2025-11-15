

import threading


class LocalizationWorker(threading.Thread):
    def __init__(self):
        super().__init__()
        self.running = True

    def run(self):
        while self.running:
            # TODO 撰寫影像辨識邏輯
            pass

    def stop(self):
        self.running = False