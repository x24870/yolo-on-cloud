import json
import numpy as np
class ModuleData:
    def __init__(self,detection_thread):
        self.detection_thread = detection_thread
        self.pc_id = ''
        self.image_height = 0
        self.image_width = 0


    def create_detection_data(self, pc_id):
        h, w = self.image_height, self.image_width
        data = {}
        data['type'] = 'detection_data'
        data['name'] = self.detection_thread.name
        #print('name: ' + str(data['name']))
        if self.detection_thread.output_datas.get(pc_id):
            data['pc_id'] = self.detection_thread.output_datas[pc_id].pc_id
            data['bbs'] = self.fix_bb_coords(self.detection_thread.output_datas[pc_id].bbs.copy(),
                                    h,w)
        #print('bbs: ' + str(data['bbs']))
            data['scores'] = self.detection_thread.output_datas[pc_id].scores.tolist()
        #print("scores: " + str(data['scores']))
            class_names = []
        #print("self.detection_thread.output_data.classes: " + str(self.detection_thread.output_data.classes))
        #print("category_index: " + str(self.detection_thread.output_data.category_index))
            for c in self.detection_thread.output_datas[pc_id].classes:
            #class_names.append(self.detection_thread.output_data.category_index.get(c)['name'])
                class_names.append(self.detection_thread.CLASS_NAMES[int(c)-1])
            data['classes'] = class_names
        #print('classes: ' + str(data['classes']))

        return data
   

    def fix_bb_coords(self,bbs,h,w):
        for indx, bb in enumerate(bbs):
            bbs[indx][0] = int(bbs[indx][0]*h)
            bbs[indx][1] = int(bbs[indx][1]*w)
            bbs[indx][2] = int(bbs[indx][2]*h)
            bbs[indx][3] = int(bbs[indx][3]*w)  

            bbs[indx][0] = max(min(bbs[indx][0],h),0)
            bbs[indx][2] = max(min(bbs[indx][2],h),0)
            bbs[indx][1] = max(min(bbs[indx][1],w),0)
            bbs[indx][3] = max(min(bbs[indx][3],w),0)
        return bbs.tolist()
    
    
    def updateData(self, message):
        # data = json.loads(message)
        try:
            self.image_height = int(message['image_properties']['height'])
            self.image_width = int(message['image_properties']['width'])
        except Exception as e:
            print("Failed loading new data." + str(e))
