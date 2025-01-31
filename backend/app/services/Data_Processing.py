import cv2
import numpy as np
import json
import robotpy_apriltag as apriltag

from config import Field
from app.services import networktables

class Tag:
    def __init__(self, id, corner):
        self.id = id
        self.corner = corner

    def to_dict(self):
        return {
            "id": self.id,
            "corner": self.corner.tolist()
        }

    def clear(self):
        self.id = None
        self.corner.clear()

class Game_piece:
    def __init__(self, type):
        self.type = type

    def to_dict(self):
        return {
            "type": self.type
        }

class Robot:
    def __init__(self, position, orientation):
        self.position = position
        self.orientation = orientation

    def to_dict(self):
        return {
            "position": self.position.tolist(),
            "orientation": self.orientation.tolist()
        }

class Data:
    def __init__(self, robot=None, tag=None, game_piece=None):
        self.robot = robot
        self.tag = tag if tag is not None else []
        self.game_piece = game_piece if game_piece is not None else []
    def clear(self):
        self.robot = None
        self.tag.clear()
        self.game_piece.clear()

    def to_dict(self):
        return {
            "robot": self.robot.to_dict() if self.robot else None,
            "tag": [t.to_dict() for t in self.tag],
            "game_piece": [g.to_dict() for g in self.game_piece]
        }

class Data_Processor:
    def __init__(self):
        self.tag_size = 0.165
        field = Field()
        self.tags_points = np.array(field.get_field_by_key('2024'), dtype=np.float64)

        self.fx = 514.6338686934114
        self.fy = 515.6938267958315
        self.cx = 312.9011223681166
        self.cy = 228.9001964935265

        self.K = np.array([
            [self.fx, 0, self.cx],
            [0, self.fy, self.cy],
            [0, 0, 1]
        ])
        self.__latest_data = Data()

    def get_latest_data(self):
        return self.__latest_data


    def upload_tag(self, data):
        self.__latest_data.tag = data
        self.processing()

    def processing(self):
        
        # 從tag計算機器資料
        data = []
        for tag in self.__latest_data.tag:


            _, rvec, tvec = cv2.solvePnP(self.tags_points[0], tag.corner, self.K, None)
            R, _ = cv2.Rodrigues(rvec)

            camera_position = -np.dot(R.T, tvec)

            pitch = np.arcsin(R[2][0])
            yaw = np.arctan2(R[1][0], R[0][0])
            roll = np.arctan2(R[2][1], R[2][2])

            data.append(Robot(
                position=camera_position,
                orientation=[pitch, yaw, roll]
            ))

        # 平均結果
        if data:
            #機器平均位置
            avg_position = np.array(np.mean([d.position for d in data], axis=0))
            networktables.update("/robot/position", avg_position.flatten().tolist())

            #機器平均方向
            avg_orientation = np.array(np.mean([d.orientation for d in data], axis=0))
            networktables.update("/robot/orientation", avg_orientation.flatten().tolist())
            
            #存至程式內存
            self.__latest_data.robot = Robot(position=avg_position, orientation=avg_orientation)
        else:
            self.__latest_data.robot = None
        
        # 計算GamePiece資料


class Detector:
    def __init__(self):
        self.tag_size = 0.165
        field = Field()
        self.tags_points = np.array(field.get_field_by_key('2024'), dtype=np.float64)

        self.fx = 514.6338686934114
        self.fy = 515.6938267958315
        self.cx = 312.9011223681166
        self.cy = 228.9001964935265

        self.K = np.array([
            [self.fx, 0, self.cx],
            [0, self.fy, self.cy],
            [0, 0, 1]
        ])

        self.detector = apriltag.AprilTagDetector()
        self.detector.addFamily("tag36h11")

        self.__data = Data()
        self.data_processor = Data_Processor()

    def detect(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect AprilTags
        results = self.detector.detect(gray)

        for result in results:
            tag_points = np.array([
                [result.getCorner(0).x, result.getCorner(0).y],
                [result.getCorner(1).x, result.getCorner(1).y],
                [result.getCorner(2).x, result.getCorner(2).y],
                [result.getCorner(3).x, result.getCorner(3).y]
            ], dtype=np.float64)
            self.__data.tag.append(
                Tag(
                    id=result.getId(),
                    corner=tag_points
                )
            )

        # upload the data to Data_Processing
        self.data_processor.upload(self.__data)
        # Return the results
        return self.__data

if __name__ == "__main__":
    detector = Detector()
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("無法打開相機")
        exit()

    while True:
        ret, frame = cap.read()
        if not ret:
            print("無法讀取影像")
            break

        detector.detect(frame)

        cv2.imshow('AprilTag Detection', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
