import numpy as np
class ImageData:
    def __init__(self, pc_id, image_np, timestamp):
        self.pc_id = pc_id
        self.image_np = image_np
        self.timestamp = timestamp
        self.can_update = True
        self.width = None
        self.height = None
        
class OutputClassificationData:
    def __init__(self):
        self.bbs = np.asarray([])
        self.score_thresh = ()
        self.scores = np.asarray([])
        self.classes = np.asarray([])
        # self.image_data = ImageData('', (), 0)
        #self.category_index = ()
        self.category_index = {}
