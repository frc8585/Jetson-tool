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

        self.detector = apriltag.AprilTagDetector()
        self.detector.addFamily("tag36h11")

        self.__data =  np.array([], dtype=Tag)

    def detect(self, frame, index):
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
        data_processor.upload_tag(self.__data, index)
        # Return the results
        return self.__data
    
