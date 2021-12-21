import json
import threading
import base64
import numpy as np
import cv2
import zmq

class Frame():
    def __init__(self, pc_id, img_np):
        self.pc_id = pc_id
        self.img_np = img_np

class ZmqImgInput(threading.Thread):
    def __init__(self, stop_evt, context, img_q):
        threading.Thread.__init__(self)
        self.stop_evt = stop_evt

        # init image message queue receiver
        self.footage_socket = context.socket(zmq.SUB)
        self.footage_socket.connect('tcp://0.0.0.0:5555')
        self.footage_socket.setsockopt_string(zmq.SUBSCRIBE, str(''))

        # queue for communicate with yolo thread
        self.img_q = img_q

        # threads of each connection ID
        self.frames = {}

    def run(self):
        print('ZmqImgInput is running!')
        self.update_img()
        
    def update_img(self):
        while not self.stop_evt.is_set():
            data = self.footage_socket.recv_json()

            # received data must contains pc_id, timestamp and image buffer
            try:
                pc_id = data['id']
                timestamp = data['timestamp']
                npimg = data['image'].encode()
            except:
                print('{} received invalid data.'.format(self.name))
                continue

            # convert image buffer to image format
            npimg = base64.b64decode(npimg)
            npimg = np.fromstring(npimg, dtype=np.uint8)
            source = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

            if not self.frames.get(pc_id):
                # create new thread for this connection
                frame = Frame(pc_id, source)
                self.frames[pc_id] = frame
            else:
                self.frames[pc_id].img_np = source

            if not self.img_q.full():
                self.img_q.put(self.frames[pc_id])

class ZmqDataHandler(threading.Thread):
    def __init__(self, stop_evt, context, res_q):
        threading.Thread.__init__(self)

        # receive detect result from this queue 
        self.res_q = res_q

        # stop event
        self.stop_evt = stop_evt

        # init data message queue sender
        self.data_socket_send = context.socket(zmq.PUB)
        self.data_socket_send.bind('tcp://*:5557')

        # init data message queue receiver
        self.data_socket_rcv = context.socket(zmq.SUB)
        self.data_socket_rcv.bind('tcp://*:5556')
        self.data_socket_rcv.setsockopt_string(zmq.SUBSCRIBE, str(''))

    def run(self):
        print('ZmqDataHandler is running')
        self.update()

    def update(self):
        while not self.stop_evt.is_set():
            try:
                # a signal to trigger getting detection result
                #_ = self.data_socket_rcv.recv_json()

                res = self.res_q.get() # class DetectionResult
                res_json = {}
                # detection raw data
                raw = 'raw'
                res_json[raw] = {}
                res_json[raw]['pc_id'] = res.pc_id
                res_json[raw]['classes'] = res.classes
                res_json[raw]['scores'] = res.scores
                res_json[raw]['bbs'] = res.bbs
                # processed cards data
                cards = 'cards'
                res_json[cards] = {}
                res_json[cards]['is_vertical'] = []
                res_json[cards]['belongs'] = []
                res_json[cards]['pattern'] = []
                res_json[cards]['confidence'] = []
                res_json[cards]['pair'] = []
                res_json[cards]['pair_centroid'] = []
                res_json[cards]['estimated_bbox'] = []
                for c in res.cards:
                    res_json[cards]['is_vertical'].append(c.is_vertical)
                    res_json[cards]['belongs'].append(c.belongs)
                    res_json[cards]['pattern'].append(c.pattern)
                    res_json[cards]['confidence'].append(c.confidence)
                    res_json[cards]['pair'].append(c.pair)
                    res_json[cards]['pair_centroid'].append(c.pair_centroid)
                    res_json[cards]['estimated_bbox'].append(c.estimated_bbox)

                # send message to websocket service
                msg = json.dumps(res_json)
                self.data_socket_send.send(f"detection_data {msg}".encode())

            except Exception as e:
                print("Error occured sending or receiving data on ML client. " + str(e))
