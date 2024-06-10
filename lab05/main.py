from DronePilot import BottleCounter, ImageReceiver
import argparse
from threading import Event, Thread
import cv2
import time

# model import and variables #

from LineDetectionModel.PathFinder import PathFinder
path_finder = PathFinder(324, 244, 30)
path_finder.load('./LineDetectionModel/pathfinder3.pth')

# drone control imports #

import logging
import sys
import time
import threading
import argparse
from threading import Event, Lock
import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.utils import uri_helper
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.crazyflie.log import LogConfig
from cflib.crazyflie.syncLogger import SyncLogger
from cflib.positioning.motion_commander import MotionCommander
from cflib.utils import uri_helper
# drone control constants #
DEFAULT_HEIGHT = 0.2
BOX_LIMIT = 0.5
URI = uri_helper.uri_from_env(default='radio://0/80/2M/E7E7E7E718')
# drone variables #
deck_attached_event = Event()
position_estimate = [0, 0]
# drone functions #
def param_deck_flow(_, value_str):
    value = int(value_str)
    print(value)
    if value:
        deck_attached_event.set()
        print('Deck is attached!')
    else:
        print('Deck is NOT attached!')

def log_pos_callback(timestamp, data, logconf):
    print(data)
    global position_estimate
    position_estimate[0] = data['stateEstimate.x']
    position_estimate[1] = data['stateEstimate.y']

def move_linear_simple(scf):
    with MotionCommander(scf, default_height=DEFAULT_HEIGHT) as mc:
        time.sleep(3)
        mc.forward(0.2)
        time.sleep(1)
        mc.back(0.2)
        time.sleep(1)

x = 0
y = 0
def move_to(scf):
    with MotionCommander(scf, default_height=DEFAULT_HEIGHT) as mc:
            mc.turn_right(90)
            print("x")
            print(x)
    return
# ---------------------- #


# img analyzer #
def image_callback(image):
    global coords
    

    preprocessed_image = path_finder.preprocess(image)
    
    # Get line coordinates
    coords = path_finder.get_line_coords(preprocessed_image)
    
    # Further processing with coords
    print(coords)
   


MAX_TIME = 40 # seconds

MAX_TIME = 40 # seconds


if __name__ == "__main__":

    cflib.crtp.init_drivers()
   
    time.sleep(1)

    parser = argparse.ArgumentParser(description='Connect to AI-deck JPEG streamer to collect images and analyze them.')
    parser.add_argument("--ip", type=str, default="192.168.4.1", help="AI-deck IP")
    parser.add_argument("--port", type=int, default='5000', help="AI-deck port")
    parser.add_argument("--confidence", type=float, default=0.2, help="Confidence threshold for bottle detection")
    parser.add_argument("--max_disappeared", type=int, default=200, help="Max number of frames an object can be missing before deregistering")
    args = parser.parse_args()

    # drone args #
    deck_port = args.port
    deck_ip = args.ip
    fetch_lock = Lock()
    # ------------ #

    image_receiver = ImageReceiver(args.ip, args.port)
    bottle_counter = BottleCounter(args.confidence, args.max_disappeared)

    image_receiver_thread = Thread(target=image_receiver.get,args=[image_callback])
    image_receiver_thread.start()

    bottle_counter_thread = Thread(target=bottle_counter.start_stream_bottle_count)
    bottle_counter_thread.start()

    #stop_event = Event()
    #key_listener_thread = Thread(target=key_listener, args=(stop_event,))
    #key_listener_thread.start()

    # drone control #
    time.sleep(2)
    with SyncCrazyflie(URI, cf=Crazyflie(rw_cache='./cache')) as scf:

        scf.cf.param.add_update_callback(group='deck', name='bcFlow2',
                                         cb=param_deck_flow)
        time.sleep(1)

        logconf = LogConfig(name='Position', period_in_ms=250)
        logconf.add_variable('stateEstimate.x', 'float')
        logconf.add_variable('stateEstimate.y', 'float')
        scf.cf.log.add_config(logconf)
        logconf.data_received_cb.add_callback(log_pos_callback)

        if not deck_attached_event.wait(timeout=5):
            print('No flow deck detected!')
            sys.exit(1)

        logconf.start()
        move_to(scf)
        logconf.stop()

    # -------------- #


    start_time = time.time()
    while time.time() - start_time < MAX_TIME:
        img = image_receiver.pop()
        if img is None:
            print("no img")
            time.sleep(0.5)
            continue
        else:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            print("Image received")
            bottle_counter.count_bottles_stream(img)

            bottle_counter.count_bottles_stream(cv2.cvtColor(img, cv2.COLOR_BRG2RGB))
            
    image_receiver.stop()
    bottle_counter.get_bottle_counter()

    image_receiver_thread.join()
    bottle_counter_thread.join()