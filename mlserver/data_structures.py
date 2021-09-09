import numpy as np
        
class DetectionResult:
    def __init__(self, pc_id, classes=np.asanyarray([]), scores=np.asanyarray([]), bbs=np.asanyarray([])):
        self.pc_id = pc_id
        self.classes = classes
        self.scores = scores
        self.bbs = bbs

