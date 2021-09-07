import threading
from queue import Queue
import base64
import numpy as np
import cv2
import base64
import zmq
from data_structures import ImageData, OutputHandler

class Frame():
    def __init__(self, pc_id, img_np):
        self.pc_id = pc_id
        self.img = img_np

class ZmqImgInput(threading.Thread):
    def __init__(self, stop_evt, context, img_q):
        threading.Thread.__init__(self)
        self.stop_evt = stop_evt

        # init image message queue receiver
        self.footage_socket = context.socket(zmq.SUB)
        self.footage_socket.bind('tcp://*:5555')
        self.footage_socket.setsockopt_string(zmq.SUBSCRIBE, str(''))

        # queue for communicate with yolo thread
        self.img_q = img_q

        # threads of each connection ID
        self.frames = {}

    def run(self):
        self.update_img()
        
    def update_img(self):
        while not self.stop_evt.is_set():
            data = self.footage_socket.recv_json()

            # received data must contains pc_id, timestamp and image buffer
            try:
                pc_id = data['pc_id']
                # timestamp = data['ts']
                npimg = data['buf'].encode()
            except:
                print('{} received invalid data.'.format(self.name))
                continue

            # convert image buffer to image format
            npimg = base64.b64decode(npimg)
            npimg = np.fromstring(npimg, dtype=np.uint8)
            source = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

            if not self.threads.get(pc_id):
                # create new thread for this connection
                frame = Frame(pc_id, source)
                self.frames[pc_id] = frame

            if not self.img_q.full():
                self.img_q.put(frame)

class ZmqDataHandler(threading.Thread):
    def __init__(self, stop_evt, context, res_q):
        # generate output data from detection result
        # self.outputHandler = OutputHandler(thread_yolo)

        # receive detect result from this queue 
        self.res_q = res_q

        # stop event
        self.stop_evt = stop_evt

        # init data message queue sender
        self.data_socket_send = context.socket(zmq.PUB)
        self.data_socket_send.connect('tcp://localhost:5557')

        # init data message queue receiver
        self.data_socket_rcv = context.socket(zmq.SUB)
        self.data_socket_rcv.bind('tcp://*:5556')
        self.data_socket_rcv.setsockopt_string(zmq.SUBSCRIBE, str(''))

    def run(self):
        self.update()

    def update(self):
        while not self.stop_evt.is_set():
            try:
                # a signal to trigger getting detection result
                _ = self.data_socket_rcv.recv_json()

                res = self.res_q.get() # class DetectionResult
                res_json = {}
                res_json['pc_id'] = res.pc_id
                res_json['classes'] = res.classes
                res_json['scores'] = res.scores
                res_json['bbs'] = res.bbs

                self.data_socket_send.send_json(res_json)
            except Exception as e:
                print("Error occured sending or receiving data on ML client. " + str(e))

class ZeroMQImageInput(threading.Thread):
    def __init__(self, context, image_lock):
        # init instance variables
        threading.Thread.__init__(self)
        self.name = "ZeroMQ Image Input Thread"
        self.image_lock = image_lock
        self.done = False

        # stores images from different source, use 'pc_id' as key
        self.images_data = {}

        # the chosen image for detection
        self.image_for_predict = ImageData('', (), 0)
        self.image_for_predict.image_np = np.zeros(shape=(608, 608, 3), dtype=np.float32)

        # init image message queue receiver
        self.footage_socket = context.socket(zmq.SUB)
        self.footage_socket.bind('tcp://*:5555')
        self.footage_socket.setsockopt_string(zmq.SUBSCRIBE, str(''))

    def run(self):
        print("Starting " + self.name)
        self.updateImg()
        print("Exiting " + self.name)

    def updateImg(self):
        while not self.done:
            data = self.footage_socket.recv_json()

            # received data must contains pc_id, timestamp and image buffer
            try:
                pc_id = data['pc_id']
                timestamp = data['ts']
                npimg = data['buf'].encode()
            except:
                print('{} received invalid data.'.format(self.name))
                continue

            # convert image buffer to image format
            npimg = base64.b64decode(npimg)
            npimg = np.fromstring(npimg, dtype=np.uint8)
            source = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
            if not self.images_data.get(pc_id):
                image_data = ImageData(pc_id, source, timestamp)
                self.images_data.setdefault(pc_id, image_data)
            else:
                self.images_data[pc_id].image_np = source
                self.images_data[pc_id].timestamp = timestamp

            # update image for prediction
            # TODO: select most recent image
            # TODO: delete image if timestamp too old
            self.image_lock.acquire()
            self.image_for_predict.pc_id = pc_id
            self.image_for_predict.image_np = self.images_data[pc_id].image_np.copy()
            self.image_for_predict.timestamp = timestamp
            self.image_lock.release()
            #cv2.imwrite('update.jpg', self.image_for_predict.image_np)

    def stop(self):
        self.done = True
        
class ZeroMQDataHandler(threading.Thread):
    def __init__(self,context, thread_yolo):
        threading.Thread.__init__(self)
        # init instance variables
        self.name = 'ZeroMQ DataHandler'
        self.done = False

        # generate output data from detection result
        self.outputHandler = OutputHandler(thread_yolo)

        # init data message queue sender
        self.data_socket_send = context.socket(zmq.PUB)
        self.data_socket_send.connect('tcp://localhost:5557')

        # init data message queue receiver
        self.data_socket_rcv = context.socket(zmq.SUB)
        self.data_socket_rcv.bind('tcp://*:5556')
        self.data_socket_rcv.setsockopt_string(zmq.SUBSCRIBE, str(''))

    def run(self):
        print("Starting " + self.name)
        self.update()
        print("Exiting " + self.name)

    def update(self):
        while not self.done:
            try:
                message = self.data_socket_rcv.recv_json()
                self.outputHandler.updateData(message)
                all_data = self.outputHandler.create_output_data(message['pc_id'])
                self.data_socket_send.send_json(all_data)
            except Exception as e:
                print("Error occured sending or receiving data on ML client. " + str(e))

    def stop(self):
        self.done = True

   
