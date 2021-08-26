import threading
import base64
import numpy as np
import cv2
import base64
import zmq
from MODULE_DATA import ModuleData
from data_structures import ImageData

class ZeroMQImageInput(threading.Thread):
    def __init__(self, context, image_lock):
        threading.Thread.__init__(self)
        self.name = "ZeroMQ Image Input Thread"
        self.images_data = {}
        self.image_for_predict = ImageData('', (), 0)
        self.image_for_predict.image_np = np.zeros(shape=(IMAGE_HEIGHT,IMAGE_WIDTH,3))
        self.done = False
        self.image_lock = image_lock

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
        self.name = 'ZeroMQ DataHandler'
        self.done = False
        self.moduleData = ModuleData(thread_yolo)
        self.data_socket_send = context.socket(zmq.PUB)
        self.data_socket_send.connect('tcp://localhost:5557')
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
                self.moduleData.updateData(message)
                all_data = self.moduleData.create_detection_data(message['pc_id'])
                self.data_socket_send.send_json(all_data)
                #print("*** Sent data: " + str(all_data))
            except Exception as e:
                print("Error occured sending or receiving data on ML client. " + str(e))

    def stop(self):
        self.done = True

   
