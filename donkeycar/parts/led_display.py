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

    def init(self):
        '''
        attempt to init gpio
        '''
        self._pi = pigpio.pi()
        self._pi.set_mode(self._redPin, pigpio.OUTPUT)
        self._pi.set_mode(self._greenPin, pigpio.OUTPUT)
        self._pi.set_mode(self._bluePin, pigpio.OUTPUT)
        return True


#    def update(self):
    def setMode(self, mode):
        if mode == 'user':
            self._pi.write(self._redPin, 0)
            self._pi.write(self._greenPin, 1)
            self._pi.write(self._bluePin, 0)
        if mode == 'local_angle':
            self._pi.write(self._redPin, 0)
            self._pi.write(self._greenPin, 0)
            self._pi.write(self._bluePin, 1)
        if mode == 'local':
            self._pi.write(self._redPin, 1)
            self._pi.write(self._greenPin, 0)
            self._pi.write(self._bluePin, 0)

    def run_threaded(self, mode):
        self.setMode(mode)

    def run(self, mode):
        self.setMode(mode)

#    def shutdown(self):

