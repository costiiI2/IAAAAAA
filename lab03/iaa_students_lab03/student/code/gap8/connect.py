
import argparse
import time
import socket,os,struct, time
import numpy as np

def args_parser():
    ### Args for setting IP/port of AI-deck.
    ### Default settings are for when AI-deck is in AP mode.
    parser = argparse.ArgumentParser(description='Connect to AI-deck JPEG streamer example')
    parser.add_argument("-n",  default="192.168.4.1", metavar="ip", help="AI-deck IP")
    parser.add_argument("-p", type=int, default='5000', metavar="port", help="AI-deck port")
    parser.add_argument('--save', action='store_true', help="Save streamed images")
    return parser.parse_args()

def main():
    args = args_parser()

    deck_port = args.p
    deck_ip = args.n

    print("Connecting to socket on {}:{}...".format(deck_ip, deck_port))
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((deck_ip, deck_port))
    print("Socket connected")

    input('<Enter> to disconnect...')

    client_socket.shutdown(SHUT_RDWR)
    client_socket.close()
    pass



if __name__ == "__main__":
    main()