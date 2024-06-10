import socket
import struct
import cv2
import numpy as np
from threading import Event
from collections import deque

class ImageReceiver():
    def __init__(self, ip, port) -> None:
        print("Connecting to socket on {}:{}...".format(ip, port))
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((ip, port))
        print("Socket connected")

        self.queue = deque()
        self.stop_event = Event()


    def _rx_bytes(self, size):
        data = bytearray()
        while len(data) < size:
            data.extend(self.client_socket.recv(size - len(data)))
        return data
    

    def get(self,image_callback):
        self.stop_event.clear()
        count = 0

        while not self.stop_event.is_set():
            packetInfoRaw = self._rx_bytes(4)
            length, _, _ = struct.unpack('<HBB', packetInfoRaw)

            imgHeader = self._rx_bytes(length - 2)
            magic, width, height, _, format, size = struct.unpack('<BHHBBI', imgHeader)

            if magic == 0xBC:
                imgStream = bytearray()
                while len(imgStream) < size:
                    packetInfoRaw = self._rx_bytes(4)
                    length, _, _ = struct.unpack('<HBB', packetInfoRaw)
                    chunk = self._rx_bytes(length - 2)
                    imgStream.extend(chunk)

                count += 1
                if format == 0:
                    bayer_img = np.frombuffer(imgStream, dtype=np.uint8)
                    bayer_img.shape = (height, width)
                    img = cv2.cvtColor(bayer_img, cv2.COLOR_BayerBG2GRAY)
                    img = img.astype(np.float64)
                    img = cv2.flip(img, 0)
                    image_callback(img)
                    self.queue.append(bayer_img)
                else:
                    with open("img.jpeg", "wb") as f:
                        f.write(imgStream)
                    nparr = np.frombuffer(imgStream, np.uint8)
                    decoded = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)
                    self.queue.append(decoded)

        print(count)


    def stop(self):
        self.stop_event.set()


    def pop(self):
        try:
            return self.queue.pop()
        except IndexError:
            return None
        
      