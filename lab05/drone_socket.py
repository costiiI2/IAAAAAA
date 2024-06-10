import argparse
import socket
import struct
import threading
import numpy as np
import cv2
from multiprocessing import Process, Queue, Event

# Args for setting IP/port of AI-deck. Default settings are for when
# AI-deck is in AP mode.
parser = argparse.ArgumentParser(description='Connect to AI-deck JPEG streamer to collect images and analyze them.')
parser.add_argument("-n", default="192.168.4.1", metavar="ip", help="AI-deck IP")
parser.add_argument("-p", type=int, default='5000', metavar="port", help="AI-deck port")
args = parser.parse_args()

deck_port = args.p
deck_ip = args.n

print("Connecting to socket on {}:{}...".format(deck_ip, deck_port))
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((deck_ip, deck_port))
print("Socket connected")


def rx_bytes(size):
    data = bytearray()
    while len(data) < size:
        data.extend(client_socket.recv(size - len(data)))
    return data


def stream_images(queue):
    count = 0

    while True:
        # First get the info
        packetInfoRaw = rx_bytes(4)
        length, _, _ = struct.unpack('<HBB', packetInfoRaw)

        imgHeader = rx_bytes(length - 2)
        magic, width, height, _, format, size = struct.unpack('<BHHBBI', imgHeader)

        if magic == 0xBC:
            imgStream = bytearray()
            while len(imgStream) < size:
                packetInfoRaw = rx_bytes(4)
                length, _, _ = struct.unpack('<HBB', packetInfoRaw)
                chunk = rx_bytes(length - 2)
                imgStream.extend(chunk)

            count += 1
            if format == 0:
                bayer_img = np.frombuffer(imgStream, dtype=np.uint8)
                bayer_img.shape = (height, width)
                cv2.imshow('Raw', bayer_img)
                queue.put(bayer_img)  # Put the image into the queue
                cv2.waitKey(1)
            else:
                with open("img.jpeg", "wb") as f:
                    f.write(imgStream)
                nparr = np.frombuffer(imgStream, np.uint8)
                decoded = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)
                cv2.imshow('JPEG', decoded)
                queue.put(decoded)  # Put the image into the queue
                cv2.waitKey(1)


def monitor_keyboard(stop_event):
    while not stop_event.is_set():
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            stop_event.set()


def analyze_images(queue):
    while not stop_event.is_set():
        if not queue.empty():
            image = queue.get()
            # Perform your image analysis here
            # For example, print the shape of the received image
            print(f"Analyzing image with shape: {image.shape}")

    print("Stopping image analysis")
    # Print number of bottles detected


if __name__ == "__main__":
    queue = Queue()
    stop_event = Event()

    stream_process = Process(target=stream_images, args=(queue, stop_event))
    analyze_process = Process(target=analyze_images, args=(queue, stop_event))

    stream_process.start()
    analyze_process.start()

    keyboard_thread = threading.Thread(target=monitor_keyboard, args=(stop_event,))
    keyboard_thread.start()

    stream_process.join()
    analyze_process.join()
    keyboard_thread.join()