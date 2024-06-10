from DronePilot import BottleCounter, ImageReceiver
import argparse
from threading import Event, Thread
import cv2
import time

def key_listener(stop_event):
    while not stop_event.is_set():
        if cv2.waitKey(1) & 0xFF == ord('q'):
            stop_event.set()
            break


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Connect to AI-deck JPEG streamer to collect images and analyze them.')
    parser.add_argument("--ip", type=str, default="192.168.4.1", help="AI-deck IP")
    parser.add_argument("--port", type=int, default='5000', help="AI-deck port")
    parser.add_argument("--confidence", type=float, default=0.2, help="Confidence threshold for bottle detection")
    parser.add_argument("--max_disappeared", type=int, default=200, help="Max number of frames an object can be missing before deregistering")
    args = parser.parse_args()

    image_receiver = ImageReceiver(args.ip, args.port)
    bottle_counter = BottleCounter(args.confidence, args.max_disappeared)

    image_receiver_thread = Thread(target=image_receiver.get)
    image_receiver_thread.start()

    bottle_counter_thread = Thread(target=bottle_counter.start_stream_bottle_count)
    bottle_counter_thread.start()

    #stop_event = Event()
    #key_listener_thread = Thread(target=key_listener, args=(stop_event,))
    #key_listener_thread.start()

    #while not stop_event.is_set():
    while True:
        img = image_receiver.pop()
        if img is None:
            time.sleep(0.5)
            continue
        else:
            bottle_counter.count_bottles_stream(img)
            
    image_receiver.stop()
    bottle_counter.get_bottle_counter()

    image_receiver_thread.join()
    bottle_counter_thread.join()
    key_listener_thread.join()

    cv2.destroyAllWindows()