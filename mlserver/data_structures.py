import numpy as np
class ImageData:
    def __init__(self, pc_id, image_np, timestamp):
        self.pc_id = pc_id
        self.image_np = image_np
        self.timestamp = timestamp
        self.width = None
        self.height = None
        
class DetectionResult:
    def __init__(self, pc_id, classes=np.asanyarray([]), scores=np.asanyarray([]), bbs=np.asanyarray([])):
        self.pc_id = pc_id
        self.classes = classes
        self.scores = scores
        self.bbs = bbs

class OutputHandler:
    def __init__(self, detection_thread):
        self.detection_thread = detection_thread
        self.image_height = 0
        self.image_width = 0

    def create_output_data(self, pc_id):
        data = {}
        data['type'] = 'detection_data'
        data['name'] = self.detection_thread.name
        if self.detection_thread.output_datas.get(pc_id):
            data['pc_id'] = self.detection_thread.output_datas[pc_id].pc_id
            data['bbs'] = self.detection_thread.output_datas[pc_id].bbs.tolist()
            data['scores'] = self.detection_thread.output_datas[pc_id].scores.tolist()
            data['classes'] = self.detection_thread.output_datas[pc_id].classes.tolist()

        return data
    
    def updateData(self, message):
        try:
            self.image_height = int(message['image_properties']['height'])
            self.image_width = int(message['image_properties']['width'])
        except Exception as e:
            print("Failed loading new data." + str(e))
