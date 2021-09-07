import warnings

from zmq.error import ZMQBaseError
warnings.filterwarnings('ignore')

import threading
from queue import Queue
from PredictorDarknet import Detector
from ZeroMQ import ZmqImgInput, ZmqDataHandler

import zmq
print("Finished Loading Imports")

import os
ROOT = os.path.dirname(os.path.realpath(__file__))

context = zmq.Context()
img_q = Queue(maxsize=1)
res_q = Queue(maxsize=1)
stop_evt = threading.Event()

thread_img = ZmqImgInput(stop_evt, context, img_q)
thread_detector = Detector(
    stop_evt,
    img_q,
    res_q,
    0.5,
    os.path.join(ROOT, 'yolov4', 'coco')
    )
thread_handler = ZmqDataHandler(stop_evt, context, res_q)

thread_img.start()
thread_detector.start()
thread_handler.start()

thread_img.join()
thread_detector.join()
thread_handler.join()

# context = zmq.Context()
# image_lock = threading.Lock()

# thread_image = ZeroMQImageInput(context, image_lock)
# thread_image.start()

# thread_yolo = DarknetYOLO(thread_image.image_for_predict,
#                             image_lock,
#                             YOLO_DIR=ROOT + "/yolov4/coco",
#                             score_thresh=0.1,fps = 0.08)
# thread_yolo.start()

# thread_zeromqdatahandler = ZeroMQDataHandler(context,thread_yolo)
# thread_zeromqdatahandler.start()
