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

        self.queue = deque() # Queue for storing images
        self.stop_event = Event() # Event for stopping the image receiver


    # Receive bytes from the socket
    def _rx_bytes(self, size):
        data = bytearray()
        while len(data) < size:
            data.extend(self.client_socket.recv(size - len(data)))
        return data
    

    # Receive images from the socket and store them in the queue
    def get(self,image_callback):
        self.stop_event.clear()
        count = 0

        # Receive images until the stop event is set
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
                # If the format is RAW, convert the image to grayscale
                if format == 0:
                    bayer_img = np.frombuffer(imgStream, dtype=np.uint8)
                    bayer_img.shape = (height, width)
                    bayer_img = cv2.flip(bayer_img,0)
                    image_callback(bayer_img)
                    
                    self.queue.append(bayer_img)
                else: # Otherwise, store the image in JPEG format as it is
                    with open("img.jpeg", "wb") as f:
                        f.write(imgStream)
                    nparr = np.frombuffer(imgStream, np.uint8)
                    decoded = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)
                    self.queue.append(decoded)


    # Stop the image receiver
    def stop(self):
        self.stop_event.set()


    # Pop an image from the queue and return it
    def pop(self):
        try:
            return self.queue.pop()
        except IndexError:
            return None
        
      