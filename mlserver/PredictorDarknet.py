import os
import threading
import time
import glob
import cv2
import numpy as np
import darknet
import pandas as pd
from data_structures import OutputClassificationData
from darknet_helper import convert2original

class DarknetYOLO(threading.Thread):
    def __init__(self, image_data, image_lock, YOLO_DIR, score_thresh, fps):
        # init YOLO required files
        print("YOLO Directory: " + YOLO_DIR)
        self.createDataFile(YOLO_DIR)
        YOLO_DATA =  glob.glob(os.path.join(YOLO_DIR,'*.data'))[0]
        YOLO_CFG =  glob.glob(os.path.join(YOLO_DIR, '*.cfg'))[0]
        YOLO_WEIGHTS =  glob.glob(os.path.join(YOLO_DIR,'*.weights'))[0]
        CLASS_NAMES =  glob.glob(os.path.join(YOLO_DIR, '*.names'))[0]
        self.createClassNames(CLASS_NAMES)

        # init instance variables
        threading.Thread.__init__(self)
        self.name = "YOLO Predictor Thread"
        self.image_lock = image_lock
        self.image_data = image_data
        self.done = False
        self.pause = False
        self.output_datas = {}
        self.score_thresh = score_thresh
        self.fps = fps

        # init darknet
        self.network, self.class_names, self.class_colors = darknet.load_network(
            YOLO_CFG,
            YOLO_DATA,
            YOLO_WEIGHTS,
            batch_size=1
        )
        self.darknet_width = darknet.network_width(self.network)
        self.darknet_height = darknet.network_height(self.network)


    def createDataFile(self, YOLO_DIR):
        FILE_DATA = os.path.join(YOLO_DIR,  os.path.basename(YOLO_DIR)+'.data')
        FILE_NAMES = glob.glob(os.path.join(YOLO_DIR, '*.names'))
        if not FILE_NAMES: 
            print("Error: can't find *.names file in '{}'".format(YOLO_DIR))
            exit()
        else:
            FILE_NAMES = FILE_NAMES[0]
        NUM_CLASSES = len(pd.read_csv(FILE_NAMES, header=None).index.values)
        f = open(FILE_DATA,"w+")
        f.write('classes= ' + str(NUM_CLASSES) + '\n')
        f.write('names= ' + str(FILE_NAMES) + '\n')
        f.close()

    def createClassNames(self, CLASS_NAMES):
        self.__BEGIN_STRING = ''
        self.CLASS_NAMES = [self.__BEGIN_STRING + str(s)
                            for s in pd.read_csv(CLASS_NAMES,header=None,names=['LabelName']).LabelName.tolist()]

        #print('CLASSE_NAMES: ' + str(self.CLASS_NAMES))
        # Remove all of the odd characters
        for indx,x in enumerate(self.CLASS_NAMES):
            if "'" in x:
                self.CLASS_NAMES[indx] = x.replace("'","")


    def predict_once(self, pc_id, image_np):
        # resize image to net size
        # image_np = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        resized_image = cv2.resize(
            image_np,
            (self.darknet_width, self.darknet_height),
            interpolation=cv2.INTER_LINEAR
            )

        # darknet only accept darknet image  
        darknet_image = darknet.make_image(self.darknet_width, darknet.network_height, 3)
        darknet.copy_image_from_bytes(darknet_image, resized_image.tobytes())

        # perform detect
        detections = darknet.detect_image(
            self.network,
            self.class_names,
            darknet_image,
            thresh=self.score_thresh
        )

        classes = []
        scores = []
        bbs = []
        for cls, score, bbox in detections:
            classes.append(cls)
            scores.append(score)
            bbox_adjusted = convert2original(
                image_np,
                bbox,
                self.darknet_height,
                self.darknet_width
                )
            bbs.append(bbox_adjusted)

        if not self.output_datas.get(pc_id):
            self.output_datas.setdefault(pc_id, OutputClassificationData())
            #TODO: delete output_data if the timestamp of the id too old
        self.output_datas[pc_id].pc_id = pc_id
        self.output_datas[pc_id].scores = scores
        self.output_datas[pc_id].classes = classes
        self.output_datas[pc_id].bbs = bbs

        # image_height,image_width,_ = image_np.shape
        # #cv2.imwrite('predict.jpg', image_np)
        # results = self.net.perform_detect(
        #     thresh=self.score_thresh,
        #     image_path_or_buf=image_np,
        #     show_image=False,
        #     make_image_only=False
        #     )
            
        # classes = []
        # scores = []
        # bbs = []
        # for r in results:
        #     classes.append(self.getLabelIndex(r.class_name))
        #     scores.append(r.class_confidence)
        #     X = r.left_x / image_width
        #     Y = r.top_y / image_width
        #     X_ = (r.left_x + r.width) / image_width
        #     Y_ = (r.top_y + r.height) / image_height
        #     bbs.append([Y, X, Y_, X_])
        # scores = np.asarray(scores)
        # classes = np.asarray(classes)
        # bbs = np.asarray(bbs)

        # if not self.output_datas.get(pc_id):
        #     self.output_datas.setdefault(pc_id, OutputClassificationData())
        #     #TODO: delete output_data if the timestamp of the id too old
        # self.output_datas[pc_id].pc_id = pc_id
        # self.output_datas[pc_id].scores = scores
        # self.output_datas[pc_id].classes = classes
        # self.output_datas[pc_id].bbs = bbs

    def predict(self):
        while not self.done:
            if not self.pause:
                self.image_lock.acquire()
                pc_id, image_np = self.getImage()
                self.predict_once(pc_id, image_np)
                self.image_lock.release()
                time.sleep(self.fps)
            else:
                self.output_data.bbs = np.asarray([])
                time.sleep(2.0) # Sleep for 2 seconds

    def run(self):
        print("Starting " + self.name)
        self.predict()
        print("Exiting " + self.name)

    def pause_predictor(self):
        self.pause = True

    def continue_predictor(self):
        self.pause = False

    def stop(self):
        self.done = True

    def getImage(self):
        '''
        Returns the image that we will use for prediction.
        '''
        return (self.image_data.pc_id, self.image_data.image_np)
