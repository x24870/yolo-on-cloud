import numpy as np
        
class DetectionResult:
    def __init__(self, pc_id, classes, scores, bbs, img, cards):
        self.pc_id = pc_id
        self.classes = classes
        self.scores = scores
        self.bbs = bbs
        self.img = img
        self.cards = cards

