
# URI to the Crazyflie to connect to

DEFAULT_HEIGHT = 0.5
BOX_LIMIT = 0.5

import logging
import sys
import time
import threading
import math
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
#from connect import Connect

import keyboard


URI = uri_helper.uri_from_env(default='radio://0/80/2M/E7E7E7E718')

deck_attached_event = Event()

logging.basicConfig(level=logging.ERROR)


position_estimate = [0, 0]

def param_deck_flow(_, value_str):
    value = int(value_str)
    print(value)
    if value:
        deck_attached_event.set()
        print('Deck is attached!')
    else:
        print('Deck is NOT attached!')

def take_off_simple(scf):
    with MotionCommander(scf, default_height=DEFAULT_HEIGHT) as mc:
        time.sleep(2)
        mc.stop()

def log_pos_callback(timestamp, data, logconf):
    print(data)
    global position_estimate
    position_estimate[0] = data['stateEstimate.x']
    position_estimate[1] = data['stateEstimate.y']

def move_linear_simple(scf):
    with MotionCommander(scf, default_height=DEFAULT_HEIGHT) as mc:
        time.sleep(3)
        mc.forward(0.5)
        time.sleep(3)
        mc.back(0.5)
        time.sleep(3)


def move_box_limit(scf):
    with MotionCommander(scf, default_height=DEFAULT_HEIGHT) as mc:
        body_x_cmd = 0.1
        body_y_cmd = 0.0
        max_vel = 1
        turn_angle = 15  # degrees
        turn_duration = 0.5 # seconds
        turn = 0

        while True:
                
                mc.circle_right(0.5, velocity=2)
                
                

MINIMAL_ANGLE_TO_TURN = 15

## TODO ADD FUNCTION TO GET ANGLE FROM CAMERA from model
def motion_with_line_detection(scf):
    with MotionCommander(scf, default_height=DEFAULT_HEIGHT) as mc:
        body_x_cmd = 0.2
        body_y_cmd = 0.0
        max_vel = 0.2
        turn_angle = 100  # degrees
        turn_duration = 2  # seconds
        angle = 0

        while True:
                ## need to got right and left angle is defined by the camera

                ## GET THE ANGLE FROM THE CAMERA alpha = get_angle()

                ## if angle is positive, turn right
                ## if angle is negative, turn left
                # turn_angle = alpha
                ## if angle is big slow down the drone else speed up

                if angle > 0:
                        if angle > MINIMAL_ANGLE_TO_TURN:
                                body_x_cmd = 0.1
                        else:
                                body_x_cmd = 0.3

                        mc.turn_right(turn_angle)
                        time.sleep(turn_duration)
                else:
                        if angle < -MINIMAL_ANGLE_TO_TURN:
                                body_x_cmd = 0.1
                        else:
                                body_x_cmd = 0.3
                        mc.turn_left(turn_angle)
                        time.sleep(turn_duration)
                mc.start_linear_motion(body_x_cmd, body_y_cmd, 0)
                time.sleep(0.1)

# Args for setting IP/port of AI-deck. Default settings are for when AI-deck is in AP mode.
parser = argparse.ArgumentParser(description='Connect to AI-deck JPEG streamer example')
parser.add_argument("-n", default="192.168.4.1", metavar="ip", help="AI-deck IP")
parser.add_argument("-p", type=int, default=5000, metavar="port", help="AI-deck port")
parser.add_argument('--save', action='store_true', help="Save streamed images")
args = parser.parse_args()

deck_port = args.p
deck_ip = args.n

fetch_lock = Lock()

# Start the fetching image thread
def start_thread(connect_obj):
    fetch_thread = threading.Thread(target=connect_obj.run)
    fetch_thread.start()
    return fetch_thread

if __name__ == '__main__':
    cflib.crtp.init_drivers()
    # Initialize the low-level drivers
    cflib.crtp.init_drivers()

    lg_stab = LogConfig(name='Stabilizer', period_in_ms=10)
    lg_stab.add_variable('stabilizer.roll', 'float')
    lg_stab.add_variable('stabilizer.pitch', 'float')
    lg_stab.add_variable('stabilizer.yaw', 'float')

    # Initialisation de l'image fetcher
    # Utilisation
    ## TODO ADD CONNECTION TO GAP8
    #connect_obj = Connect(deck_ip, deck_port, args.save, line_coords, coords_lock)
    #fetch_thread = start_thread(connect_obj)

    time.sleep(1)

    with SyncCrazyflie(URI, cf=Crazyflie(rw_cache='./cache')) as scf:

        scf.cf.param.add_update_callback(group='deck', name='bcFlow2',
                                         cb=param_deck_flow)
        time.sleep(1)

        logconf = LogConfig(name='Position', period_in_ms=10)
        logconf.add_variable('stateEstimate.x', 'float')
        logconf.add_variable('stateEstimate.y', 'float')
        scf.cf.log.add_config(logconf)
        logconf.data_received_cb.add_callback(log_pos_callback)

        if not deck_attached_event.wait(timeout=5):
            print('No flow deck detected!')
            sys.exit(1)

        logconf.start()
        #move_linear_simple(scf)
        move_box_limit(scf)
        logconf.stop()