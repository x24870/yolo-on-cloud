import os
import threading
import glob
import cv2
import numpy as np
import darknet
import pandas as pd
from data_structures import DetectionResult
from darknet_helper import convert2original
import Barccarat
import Card_processor as cardp

class Detector(threading.Thread):
    def __init__(self, stop_evt, img_q, res_q, score_thresh, YOLO_DIR):
        self.createDataFile(YOLO_DIR)
        YOLO_DATA =  glob.glob(os.path.join(YOLO_DIR,'cards.data'))[0]
        YOLO_CFG =  glob.glob(os.path.join(YOLO_DIR, 'yolov4-custom.cfg'))[0]
        YOLO_WEIGHTS =  glob.glob(os.path.join(YOLO_DIR,'yolov4-custom_35000.weights'))[0]
        CLASS_NAMES =  glob.glob(os.path.join(YOLO_DIR, '*.names'))[0]
        self.createClassNames(CLASS_NAMES)
        # init instance variables
        threading.Thread.__init__(self)
        self.stop_evt = stop_evt
        self.img_q = img_q
        self.res_q = res_q
        self.score_thresh = score_thresh
        self.baccarat = Barccarat()

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

    def run(self):
        self.detect()

    def detect(self):
        while not self.stop_evt.is_set():
            frame = self.img_q.get()
            print("got frame")
            self.detect_once(frame.pc_id, frame.img_np)


    def detect_once(self, pc_id, img_np):
        # perspective transform
        H, W = img_np.shape[:2]
        pspect = -200
        pts1 = np.float32([[0, 0], [W, 0], [0, H], [W, H]])
        pts2 = np.float32([[pspect,0], [W-pspect, 0], [0, H], [W, H]])
        #pts2 = np.float32([[0, 0], [W, 0], [pspect, H], [W-pspect, H]])
        M = cv2.getPerspectiveTransform(pts1, pts2)
        img_np = cv2.warpPerspective(img_np, M, (W, H))

        # crop img
        #y = int(img_np.shape[0]/4)
        #x = int(img_np.shape[1]/4)
        #w = x*2
        #h = y*2
        #img_np = img_np[y:y+h, x:x+w]

        # convert to RGB channel and resize image to net size
        rgb_image = cv2.cvtColor(img_np, cv2.COLOR_BGR2RGB)
        resized_image = cv2.resize(
            rgb_image,
            (self.darknet_width, self.darknet_height),
            interpolation=cv2.INTER_LINEAR
            )

        # darknet only accept darknet image  
        darknet_image = darknet.make_image(self.darknet_width, self.darknet_height, 3)
        darknet.copy_image_from_bytes(darknet_image, resized_image.tobytes())

        # perform detect
        detections = darknet.detect_image(
            self.network,
            self.class_names,
            darknet_image,
            thresh=self.score_thresh
        )

        # release darknet image
        darknet.free_image(darknet_image)

        if not detections: return

        classes = []
        scores = []
        bbs = []
        for cls, score, bbox in detections:
            classes.append(cls)
            scores.append(score)
            bbox_adjusted = convert2original(
                img_np,
                bbox,
                self.darknet_height,
                self.darknet_width
                )
            left, top, right, buttom = darknet.bbox2points(bbox_adjusted)
            #bbs.append([left, top, right, buttom]) #TODO: Modify frontend to comply this order
            bbs.append([top, left, buttom, right])

        print('class: {}, score: {}'.format(classes, scores))

        # baccarat
        cards = cardp.process_cards_info(detections)

        res = DetectionResult(
            pc_id,
            classes,
            scores,
            bbs,
            img_np,
            cards
            )

        if not self.res_q.full():
            self.res_q.put(res)


