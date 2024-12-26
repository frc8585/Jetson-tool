import cv2
import numpy as np
import robotpy_apriltag as apriltag
from threading import Thread, Event

from app.services import detector
from config import Field

class Image_Processing:
    def __init__(self):
        self.tag_size = 0.165
        field = Field()
        self.tags_points = np.array(field.get_field_by_key('2024'), dtype=np.float64)

        self.index = 1

        self.color = [(0, 0, 255), (0, 255, 0), (255, 0, 0), (255, 0, 0)]

        self.latest_data = None

        self.running_event = Event()
        self.thread = None

    def _run(self):
        cap = cv2.VideoCapture(self.index)

        if not cap.isOpened():
            print("無法打開相機")
            return

        self.running_event.set()

        while self.running_event.is_set():
            ret, frame = cap.read()
            if not ret:
                print("無法讀取影像")
                break

            results = detector.detect(frame)

            
            if results != []:
                for result in results:
                    for i in range(4):
                        pt1 = np.round(result.corner[i]).astype(int)
                        pt2 = np.round(result.corner[(i + 1) % 4]).astype(int)
                        cv2.line(frame, tuple(pt1), tuple(pt2), self.color[i], 2)

                    cv2.putText(frame, f"ID: {result.id}", (int(result.corner[0][0]), int(result.corner[0][1]) - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            # Show the frame
            cv2.imshow('AprilTag Detection', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.stop()
                break

        cap.release()
        cv2.destroyAllWindows()

    def run(self):
        if self.thread is None or not self.thread.is_alive():
            self.thread = Thread(target=self._run)
            self.thread.start()

    def stop(self):
        self.running_event.clear()
        if self.thread is not None:
            self.thread.join()
        cv2.destroyAllWindows()