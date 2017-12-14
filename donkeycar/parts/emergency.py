#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wen Dec 06 15:29:44 2017

@author: bznoit.trinite

txwcontroller.py


"""



import array
import time
import struct
from threading import Thread
import donkeycar as dk
from socket import *

class EmergencyController(object):
    '''
    Emergency Ctrl
    '''

    def __init__(self, poll_delay=0.0,
                 verbose = False
                 ):

        self.verbose = verbose
        self.socket = None
        self.running = True
        self.user_mode = "user"
        self.poll_delay = poll_delay

    def init_socket(self):
        '''
        attempt to init listening socket
        '''
        self.socket=socket(AF_INET, SOCK_DGRAM)
        self.socket.bind(('',12345))

        return self.socket is not None


    def update(self):
        '''
        poll for emergency events
        '''

        #wait for Tx to be online
        while self.running and not self.init_socket():
            time.sleep(5)

        while self.running:
            self.msg,self.addr =self.socket.recvfrom(1024)
            text = self.msg.decode('ascii')
            if not self.msg:
                break
            if ('STOP'==text):
                print ("Get emergency signal :"+text)
                if(self.requested_user_mode != "user"):
                    print("STOP the vehicule !")
                    self.user_mode="user"
            time.sleep(self.poll_delay)

    def run_threaded(self, img_arr=None, user_mode=None):
        self.img_arr = img_arr
        self.requested_user_mode = user_mode
        return self.user_mode

    def run(self, img_arr=None, user_mode=None):
        raise Exception("We expect for this part to be run with the threaded=True argument.")
        return False

    def shutdown(self):
        self.running = False
        time.sleep(0.5)

