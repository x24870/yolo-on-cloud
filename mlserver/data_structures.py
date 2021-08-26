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
        self.pc_id = ''
        self.bbs = np.asarray([])
        self.scores = np.asarray([])
        self.classes = np.asarray([])
        self.category_index = {}
