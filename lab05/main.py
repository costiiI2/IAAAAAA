from DronePilot import BottleCounter, ImageReceiver
import argparse
from threading import Event, Thread
import cv2
import time

# model import and variables #

from LineDetectionModel.PathFinder import PathFinder
path_finder = PathFinder(324, 244, 30)
path_finder.load('./LineDetectionModel/pathfinder3.pth')


MAX_TIME = 4 # seconds

running = True
# drone control imports #

import math
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
     #print(data)
    global position_estimate
    position_estimate[0] = data['stateEstimate.x']
    position_estimate[1] = data['stateEstimate.y']

r=0
l=0
calculated_angle = 0
direction = 'gg'
coords=[0,0,0]
def compute_steering_angle(steering_vector):
    x1, x2, y2 = steering_vector
    y1 = 244  # y1 is always 244

    # Calculate the angle in radians relative to the vertical axis
    angle_rad = math.atan2(x2 - x1, y1 - y2)
    
    # Convert angle to degrees
    angle_deg = math.degrees(angle_rad)
    
    # Normalize the angle to the range [-180, 180]
    if angle_deg < -180:
        angle_deg += 360
    elif angle_deg > 180:
        angle_deg -= 360
    
    # Determine the direction
    if angle_deg > 0:
        direction = 'right'
    else:
        direction = 'left'

    # Security check, avoid our drone turn into a bayblade
    if(abs(angle_deg) > 90):
        angle_deg = 90
    
    return abs(angle_deg), direction

def move_to(scf):
    with MotionCommander(scf, default_height=DEFAULT_HEIGHT) as mc:
        time.sleep(1)
        start_time = time.time()
        global l,r
        
        while time.time() - start_time < MAX_TIME:
                # si x1 de coord est pass au  millieubouge
                if(coords[0] < 100):
                    print("moving left +")
                    mc.move_distance(0,0.2,0,0.1)
                elif(coords[0] > 220):
                    print("moving left -")
                    mc.move_distance(0,-0.2,0,0.1)
                if(r > 3):
                    print("circle rigth")
                    mc.circle_right(0.2,0.1,20)
                    r = 0
                    l = 0
                elif(l > 3):
                    print("circle ri^left")
                    mc.circle_left(0.2,0.1,20)
                    r=0
                    l=0
                else:
                    print("move")
                    mc.move_distance(0.1,0,0,0.2)
    return
# ---------------------- #
def stationary(scf):
    with MotionCommander(scf, default_height=DEFAULT_HEIGHT) as mc:  
        time.sleep(1)
        start_time = time.time()
        global l,r
        
        while time.time() - start_time < MAX_TIME:
            mc.circle_left(0.2,0.2)  
        print("done flying")


def move_box_limit(scf):
    with MotionCommander(scf, default_height=DEFAULT_HEIGHT) as mc:        
        mc.move_distance(0.2,0,0,velocity=0.5)
        mc.turn_right(35)

        mc.move_distance(0.2,0,0,velocity=0.2)

        mc.turn_left(40)

        mc.move_distance(0.5,0,0,velocity=0.2)
        mc.turn_left(40)
        mc.move_distance(0.5,0,0,velocity=0.2)
        mc.turn_left(40)
        mc.move_distance(0.5,0,0,velocity=0.2)
        mc.turn_left(60)
        mc.move_distance(0.5,0,0,velocity=0.2)
        mc.turn_left(40)
        mc.move_distance(0.5,0,0,velocity=0.2)
        mc.turn_right(20)
        mc.move_distance(0.2,0,0,velocity=0.2)
        mc.turn_right(20)
        mc.move_distance(0.7,0,0,velocity=0.2)
        mc.turn_left(40)
        mc.move_distance(0.5,0,0,velocity=0.2)
        mc.turn_left(40)
        mc.move_distance(0.6,0,0,velocity=0.2)
        mc.turn_left(40)                
        mc.move_distance(0.5,0,0,velocity=0.2)
        mc.turn_left(40)
        mc.move_distance(0.5,0,0,velocity=0.2)
        mc.turn_left(75)
        mc.move_distance(0.9,0,0,velocity=0.2)

# img analyzer #
def image_callback(image):
    global coords
    imgc = cv2.cvtColor(image, cv2.COLOR_BayerBG2GRAY)
    img = imgc.astype("float64")

    preprocessed_image = path_finder.preprocess(img)


    # Get line coordinates
    coords = path_finder.get_line_coords(preprocessed_image)
    
    # Further processing with coords
    a,b = compute_steering_angle(coords)    
    global calculated_angle 
    global direction
    calculated_angle = a
    direction = b
    global r,l
    if(direction == 'right'):
        r += 1
    elif(direction == 'left'):
        l += 1
    print(f'Angle: {calculated_angle}, Direction: {direction}')
   

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

        logconf = LogConfig(name='Position', period_in_ms=2000)
        logconf.add_variable('stateEstimate.x', 'float')
        logconf.add_variable('stateEstimate.y', 'float')
        scf.cf.log.add_config(logconf)
        logconf.data_received_cb.add_callback(log_pos_callback)

        if not deck_attached_event.wait(timeout=5):
            print('No flow deck detected!')
            sys.exit(1)


    # -------------- #


        start_time = time.time()
        logconf.start()
        #move_to(scf)
        move_box_limit(scf)
        #stationary(scf)
        logconf.stop()

        

        
        
        img = image_receiver.pop() 
        i = 0
        while img is not None:
                print("Image received")
                print(i)
                i += 1
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                bottle_counter.count_bottles_stream(img)
                #save img
                cv2.imwrite(f'./img_{i}.jpeg', img)
                img = image_receiver.pop() 
          
        image_receiver.stop()
        bottle_counter.get_bottle_counter()

        image_receiver_thread.join()
        bottle_counter_thread.join()
