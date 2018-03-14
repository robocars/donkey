#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 04 15:29:44 2018

@author: cristian.nitescu

led_display.py


"""



import array
import time
import struct
from threading import Thread
import donkeycar as dk
from sys import platform

import pigpio

class LedDisplay(object):
    '''
    Tx client using access to local serial input
    '''

    def __init__(self, 
                 red_pin=21,
                 green_pin=20,
                 blue_pin=19
                 ):

        self._pi = None;
        self._redPin = red_pin
        self._greenPin = green_pin
        self._bluePin = blue_pin

#    def init(self):
        '''
        attempt to init gpio
        '''
        self._pi = pigpio.pi()
        self._pi.set_mode(self._redPin, pigpio.OUTPUT)
        self._pi.set_mode(self._greenPin, pigpio.OUTPUT)
        self._pi.set_mode(self._bluePin, pigpio.OUTPUT)
#        return True


#    def update(self):
#        while not self.init():
#           time.sleep(1)

    def setMode(self, mode, throttle):
        on_state = 1
        if (throttle > 0.1) or (throttle < -0.1):
            on_state = int(round(time.time()))
            on_state = on_state % 2
        if mode == 'user':
            self._pi.write(self._redPin, 0)
            self._pi.write(self._greenPin, on_state)
            self._pi.write(self._bluePin, 0)
        if mode == 'local_angle':
            self._pi.write(self._redPin, 0)
            self._pi.write(self._greenPin, 0)
            self._pi.write(self._bluePin, on_state)
        if mode == 'local':
            self._pi.write(self._redPin, on_state)
            self._pi.write(self._greenPin, 0)
            self._pi.write(self._bluePin, 0)

    def run_threaded(self, mode, throttle):
        self.setMode(mode, throttle)

    def run(self, mode, throttle):
        self.setMode(mode, throttle)

#    def shutdown(self):

