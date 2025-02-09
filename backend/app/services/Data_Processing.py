import cv2
import numpy as np
import json
import robotpy_apriltag as apriltag

from config import Field

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
    def __init__(self, position, orientation, revc, tvec):
        self.position = position
        self.orientation = orientation
        self.revc = revc
        self.tvec = tvec

    def to_dict(self):
        return {
            "position": self.position.tolist(),
            "orientation": self.orientation.tolist(),
            "revc": self.revc.tolist() if self.revc is not None else None,
            "tvec": self.tvec.tolist() if self.tvec is not None else None
        }

class Data:
    def __init__(self, robot=None, tags=None, game_piece=None):
        self.robot = robot
        self.tag = tags if tags is not None else {}
        self.game_piece = game_piece if game_piece is not None else []
    def clear(self):
        self.robot = None
        self.tag = {}
        self.game_piece.clear()

    def to_dict(self):
        tags = {}
        for index, tag in self.tag:
            tags[index] = tag.to_dict()
        return {
            "robot": self.robot.to_dict() if self.robot else None,
            "tag": {tags},
            "game_piece": [g.to_dict() for g in self.game_piece]
        }

class Data_Processor:
    def __init__(self):
        self.tag_size = 0.165
        field = Field()
        self.tags_points = np.array(field.get_field_by_key('2025').get("Tags"), dtype=np.float64)

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


    def upload_tag(self, data, index):
        self.__latest_data.tag[index] = data
        self.processing()

    def processing(self):
        
        # 從tag計算機器資料
        data = []
        for index, tags in self.__latest_data.tag.items():
            for tag in tags:

                _, rvec, tvec = cv2.solvePnP(self.tags_points[tag.id], tag.corner, self.K, None)
                R, _ = cv2.Rodrigues(rvec)

                camera_position = -np.dot(R.T, tvec)

                pitch = np.arcsin(R[2][0])
                yaw = np.arctan2(R[1][0], R[0][0])
                roll = np.arctan2(R[2][1], R[2][2])

                data.append(Robot(
                    position=camera_position,
                    orientation=[pitch, yaw, roll],
                    revc=rvec,
                    tvec=tvec
                ))

        # 平均結果
        if data:
            avg_position = np.mean([d.position for d in data], axis=0)
            avg_orientation = np.mean([d.orientation for d in data], axis=0)
            self.__latest_data.robot = Robot(position=avg_position, orientation=avg_orientation, revc=rvec, tvec=tvec)
        else:
            self.__latest_data.robot = None
        
        # 計算GamePiece資料

