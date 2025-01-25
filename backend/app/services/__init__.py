from threading import Thread
from .Data_Processing import Data_Processor, Data, Tag, Robot
data_processor = Data_Processor()

from .Detector import Detector
detector = Detector()

from .Image_Processing import Image_Processing
image_processing = Image_Processing()

from .NetworkTables import NetworkTables
network_tables = NetworkTables()
