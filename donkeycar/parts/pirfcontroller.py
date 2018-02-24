#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 04 15:29:44 2018

@author: cristian.nitescu

pirfcontroller.py


"""



import array
import time
import struct
from threading import Thread
import donkeycar as dk
from sys import platform

import pigpio

import logging
logger = logging.getLogger('donkey.pirfctrl')

if platform != "darwin":
    import serial

def map_range(x, X_min, X_max, Y_min, Y_max):
    '''
    Linear mapping between two ranges of values
    '''
    if (x<X_min):
        x=X_min
    if (x>X_max):
        x=X_max
    X_range = X_max - X_min
    Y_range = Y_max - Y_min
    XY_ratio = X_range/Y_range

    y = ((x-X_min) / XY_ratio + Y_min)

    return y

class PWMReader():
    def __init__(self, pi, pin):
        self._pi = pi
        self._pin = pin
        
        self._high = None
        self._low = None
        self.timeHigh = None
        self.timeLow = None
        
        self._pin_mode = pi.get_mode(self._pin)
        pi.set_mode(self._pin, pigpio.INPUT)
        pi.set_pull_up_down(self._pin, pigpio.PUD_UP)
        self._cb = pi.callback(self._pin, pigpio.EITHER_EDGE, self._cbf)

        self._inited = True
    def _cbf(self, gpio, level, tick):
        if level == 1:
            self._high = tick
            if self._low is not None:
                self.timeLow = tick - self._low
                self._low = None
        else:
            self._low = tick
            if self._high is not None:
                self.timeHigh = tick - self._high
                self._high = None

    def cancel(self):
        """
        Cancels the ranger and returns the gpios to their
        original mode.
        """
        if self._inited:
            self._inited = False
            self._cb.cancel()
            self._pi.set_mode(self._pin, self._pin_mode)

class PiRfController(object):
    '''
    Tx client using access to local serial input
    '''

    def __init__(self, poll_delay=0.0,
                 throttle_tx_min=913,
                 throttle_tx_max=2111,
                 steering_tx_min=955,
                 steering_tx_max=2085,
                 throttle_tx_thresh=1520,
                 steering_pin=23,
                 throttle_pin=18,
                 change_mode_pin=22,
                 auto_record_on_throttle=True,
                 verbose = False
                 ):

        self.angle = 0.0
        self.throttle = 0.0
        self.mode = 'user'
        self._crt_mode = 0
        self.poll_delay = poll_delay
        self.running = True
        self.throttle_tx_thresh = throttle_tx_thresh
        self.throttle_tx_min = throttle_tx_min
        self.throttle_tx_max = throttle_tx_max
        self.steering_tx_min = steering_tx_min
        self.steering_tx_max = steering_tx_max

        self.recording = False
        self.auto_record_on_throttle = auto_record_on_throttle
        self._pi = None;
        self._steeringPin = steering_pin
        self._throttlePin = throttle_pin
        self._changeModePin = change_mode_pin
        self._steeringPwm = None
        self._throttlePwm = None
        self._changeModePwm = None
        self._ready_change_mode = True
        self.verbose = verbose

    def on_throttle_changes(self):
        '''
        turn on recording when non zero throttle in the user mode.
        '''
        if self.auto_record_on_throttle:
            self.recording = (self.throttle != 0.0 and self.mode == 'user')

    def next_mode(self):
        modes = ['user', 'local_angle', 'local']
        self._crt_mode = (self._crt_mode + 1) % 3
        self.mode = modes[self._crt_mode]

    def init(self):
        '''
        attempt to init Tx
        '''
        self._pi = pigpio.pi()
        self._steeringPwm = PWMReader(self._pi, self._steeringPin)
        self._throttlePwm = PWMReader(self._pi, self._throttlePin)
        self._changeModePwm = PWMReader(self._pi, self._changeModePin)
        return True


    def update(self):
        #wait for Tx to be online
        while self.running and not self.init():
            time.sleep(5)

        while self.running:
            throttle_tx = self._throttlePwm.timeHigh
            if throttle_tx == None:
                throttle_tx = 1500
            steering_tx = self._steeringPwm.timeHigh
            if steering_tx == None:
                steering_tx = 1500
            change_mode_tx = self._changeModePwm.timeHigh
            if change_mode_tx == None or change_mode_tx < 1500:
                self._ready_change_mode = True
            else:
                if self._ready_change_mode:
                    self.next_mode()
                self._ready_change_mode = False
            freq_tx = 60
#            if throttle_tx > self.throttle_tx_thresh:
#                self.throttle = map_range(throttle_tx, self.throttle_tx_min, self.throttle_tx_max, -1, 1)
#            else:
#                self.throttle = 0
            self.throttle = map_range(throttle_tx, self.throttle_tx_min, self.throttle_tx_max, -1, 1)
            self.on_throttle_changes()
            self.angle = map_range(steering_tx, self.steering_tx_min, self.steering_tx_max, -1, 1)
            logger.info('angle= {:01.2f} throttle= {:01.2f}'.format(self.angle, self.throttle))
            if self.verbose:
                print('angle= {:01.2f} throttle= {:01.2f}'.format(self.angle, self.throttle))
            time.sleep(self.poll_delay)

    def run_threaded(self, img_arr=None):
        self.img_arr = img_arr
        return self.angle, self.throttle, self.mode, self.recording

    def run(self, img_arr=None):
        raise Exception("We expect for this part to be run with the threaded=True argument.")
        return False

    def shutdown(self):
        self.running = False
        self._steeringPwm.cancel()
        self._throttlePwm.cancel()
        self._changeModePwm.cancel()
        time.sleep(0.5)

