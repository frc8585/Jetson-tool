import cv2
import numpy as np
import robotpy_apriltag as apriltag
from threading import Thread, Event

from app.services import detector, data_processor
from config import Field

class Image_Processing:
    def __init__(self):
        self.tag_size = 0.165
        field = Field()
        self.tags_points = np.array(field.get_field_by_key('2025').get("Tags"), dtype=np.float64)

        self.field = np.array(field.get_field_by_key('2025').get("Field"))

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
                    
                    for field in self.field:
                        
                        if result.id in field["Tags"]:
                            for name,child in field["child"].items():
                                match child["shape"]:
                                    case "rectangle":
                                        cv2.rectangle(frame, (child["x"], child["y"]), (child["x"] + child["w"], child["y"] + child["h"]), (0, 255, 0), 2)
                                    case "circle":
                                        self.draw_circle(frame, child["center"], child["r"], child["normal"], (0, 255, 0), 2)    
                                    case _:
                                        print("Unknown shape")
                            break

            # Show the frame
            cv2.imshow('AprilTag Detection', frame)

            cv2.waitKey(1)
                

        cap.release()
        cv2.destroyAllWindows()

    def draw_circle(self, frame, center, radius, normal_vector, color=(0, 255, 0), thickness=2):
        center = np.array(center).astype(np.float64)
        radius = np.float64(radius)
        normal_vector = np.array(normal_vector).astype(np.float64)
        rvec = data_processor.get_latest_data().robot.revc
        tvec = data_processor.get_latest_data().robot.tvec
        K = data_processor.K

        center_2, _ = cv2.projectPoints(center, rvec, tvec, K, distCoeffs=None)

        cv2.circle(frame, tuple(center_2.ravel().astype(int)), 10, color, thickness)

    def run(self):
        if self.thread is None or not self.thread.is_alive():
            self.thread = Thread(target=self._run)
            self.thread.start()

    def stop(self):
        self.running_event.clear()
        if self.thread is not None:
            self.thread.join()
        cv2.destroyAllWindows()