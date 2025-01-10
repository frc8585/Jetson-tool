import cv2
import numpy as np
import robotpy_apriltag as apriltag

from app.services import Data, Tag
from app.services import data_processor
from config import Field

class Detector:
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

        self.detector = apriltag.AprilTagDetector()
        self.detector.addFamily("tag36h11")

        self.__data =  np.array([], dtype=Tag)

    def detect(self, frame):
        self.__data = []
        
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
            self.__data.append(
                Tag(
                    id=result.getId(),
                    corner=tag_points
                )
            )

        # Detect GamePieces


        # upload the data to Data_Processing
        data_processor.upload_tag(self.__data)
        # Return the results
        return self.__data
    
