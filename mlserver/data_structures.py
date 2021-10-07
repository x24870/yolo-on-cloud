import numpy as np
        
class DetectionResult:
    def __init__(self, pc_id, classes, scores, bbs, cropped_img):
        self.pc_id = pc_id
        self.classes = classes
        self.scores = scores
        self.bbs = bbs
        self.cropped_img = cropped_img

