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
import serial

#import for syntactical ease
from donkeycar.parts.web_controller.web import LocalWebController

class Txserial():
    '''
    An interface to a Tx through serial link
    '''
    def __init__(self):
        self.ser = null

    def init(self):
        # Open serial link
        seld.ser = serial.Serial(
              
               port='/dev/ttyAMA0',
               baudrate = 9600,
               parity=serial.PARITY_NONE,
               stopbits=serial.STOPBITS_ONE,
               bytesize=serial.EIGHTBITS,
               timeout=1
        )
        '''
        Add a check on received values 
        '''
        return True

    def poll(self):
        '''
        query the state of the joystick, returns button which was pressed, if any,
        and axis which was moved, if any. button_state will be None, 1, or 0 if no changes, 
        pressed, or released. axis_val will be a float from -1 to +1. button and axis will 
        be the string label determined by the axis map in init.
        '''
        throttle_tx = None
        steering_tx = None
        freq_tx = None

        x=self.ser.readline()

        '''
        TODO par line to extract throttle, steering and freq
        format is <throttle_pwm>,<steering_pwm>,<freq_pwm>
        throttle_pwm and steering_pwm are in us
        freq_pwm is in Hz.
        Should we normalize here ?
        (1/freq_pwm)*1000000 -> pwm_period
        throttle = ((throttle_pwm-(pwm_period/2))/(pwm_period/2)
        steering = ((steering_pwm-(pwm_period/2))/(pwm_period/2)
        for sure, filtering is needed for throttle (we know that reverse throttle is not usefull, we can implement a simple threshold)
        '''

        return throttle_tx, steering_tx, freq_tx


class TXController(object):
    '''
    Tx client using access to local serial input
    '''

    def __init__(self, poll_delay=0.0,
                 max_throttle=1.0,
                 steering_scale=1.0,
                 throttle_scale=1.0,
                 auto_record_on_throttle=True,
                 verbose = False
                 ):

        self.angle = 0.0
        self.throttle = 0.0
        self.mode = 'user'
        self.poll_delay = poll_delay
        self.running = True
        self.max_throttle = max_throttle
        self.recording = False
        self.auto_record_on_throttle = auto_record_on_throttle
        self.tx = None
        self.verbose = verbose

    def on_throttle_changes(self):
        '''
        turn on recording when non zero throttle in the user mode.
        '''
        if self.auto_record_on_throttle:
            self.recording = (self.throttle != 0.0 and self.mode == 'user')

    def init_tx(self):
        '''
        attempt to init Tx
        '''
        try:
            self.tx = Txserial()
            self.tx.init()
        except FileNotFoundError:
            print(" Unable to init Tx receiver.")
            self.tx = None
        return self.tx is not None


    def update(self):
        '''
        poll a Tx for input events
        '''

        #wait for Tx to be online
        while self.running and not self.init_tx():
            time.sleep(5)

        while self.running:
            throttle_tx, steering_tx, freq_tx = self.tx.poll()

            '''
            TODO : map throttle and steering which are PWM data into ratio.
            then update self.steering and self.throttle.
            If throttle change, call on_throttle_changes
            '''

            time.sleep(self.poll_delay)

    def run_threaded(self, img_arr=None):
        self.img_arr = img_arr
        return self.steering, self.throttle, self.mode, self.recording

    def run(self, img_arr=None):
        raise Exception("We expect for this part to be run with the threaded=True argument.")
        return False

    def shutdown(self):
        self.running = False
        time.sleep(0.5)

