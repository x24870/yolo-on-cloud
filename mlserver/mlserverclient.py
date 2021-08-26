import warnings
warnings.filterwarnings('ignore')

import threading
from PredictorDarknet import DarknetYOLO
from ZeroMQ import ZeroMQDataHandler
from ZeroMQ import ZeroMQImageInput

import zmq
print("Finished Loading Imports")

import os
ROOT = os.path.dirname(os.path.realpath(__file__))

context = zmq.Context()
image_lock = threading.Lock()

thread_image = ZeroMQImageInput(context);
thread_image.start()

thread_yolo = DarknetYOLO(thread_image.image_for_predict,
                        YOLO_DIR=ROOT + "/yolov4/coco",
                        score_thresh=0.1,
                        fps = 0.08)
thread_yolo.start()

thread_zeromqdatahandler = ZeroMQDataHandler(context,thread_yolo)
thread_zeromqdatahandler.start()
