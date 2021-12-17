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
    0.7,
    os.path.join(ROOT, 'yolov4', 'cards')
    )
thread_handler = ZmqDataHandler(stop_evt, context, res_q)

thread_img.start()
thread_detector.start()
thread_handler.start()

thread_img.join()
thread_detector.join()
thread_handler.join()
