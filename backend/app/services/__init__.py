from threading import Thread
from .Data_Processing import Data_Processor, Data, Tag, Robot
data_processor = Data_Processor()

from .Detector import Detector
detector = Detector()

from .Zed import Zed
zed = Zed()

from .Image_Processing import Image_Processing
image_processing = Image_Processing()
