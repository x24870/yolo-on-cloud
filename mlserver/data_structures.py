import numpy as np
class ImageData:
    def __init__(self, image_np, timestamp):
        self.image_np = image_np
        self.timestamp = timestamp
        self.isInit = False
        self.width = None
        self.height = None
        
class OutputClassificationData:
    def __init__(self):
        self.bbs = np.asarray([])
        self.score_thresh = ()
        self.scores = np.asarray([])
        self.classes = np.asarray([])
        self.image_data = ImageData((), 0)
        #self.category_index = ()
        self.category_index = {}
