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
logger = logging.getLogger('donkey.sonar')

class SonarReader():
    def __init__(self, pi, pinTrig, pinEcho):
        self._pi = pi
        self._trig = pinTrig
        self._echo = pinEcho

        self._ping = False
        self._high = None
        self._time = None

        self._triggered = False
        
        #self._pin_mode = pi.get_mode(self._pin)
        pi.set_mode(self._trig, pigpio.OUTPUT)
        pi.set_mode(self._echo, pigpio.INPUT)
        self._cb = pi.callback(self._trig, pigpio.EITHER_EDGE, self._cbf)
        self._cb = pi.callback(self._echo, pigpio.EITHER_EDGE, self._cbf)

        self._inited = True
    def _cbf(self, gpio, level, tick):
        if gpio == self._trig:
            if level == 0: # trigger sent
                self._triggered = True
                self._high = None
        else:
            if self._triggered:
                if level == 1:
                    self._high = tick
                else:
                    if self._high is not None:
                        self._time = tick - self._high
                        self._high = None
                        self._ping = True

    def read(self):
        """
        Triggers a reading.  The returned reading is the number
        of microseconds for the sonar round-trip.

        round trip cms = round trip time / 1000000.0 * 34030
        """
        if self._inited:
            self._ping = False
            self._pi.gpio_trigger(self._trig)
            start = time.time()
            while not self._ping:
                if (time.time()-start) > 5.0:
                    return 20000
                time.sleep(0.001)
            return self._time
        else:
            return None

    def cancel(self):
        """
        Cancels the ranger and returns the gpios to their
        original mode.
        """
        if self._inited:
            self._inited = False
            self._cb.cancel()

class SonarController(object):
    '''
    Tx client using access to local serial input
    '''

    def __init__(self, poll_delay=0.0,
                 trigger_pin=24,
                 echo_pin=25,
                 slowdown_limit=6000,
                 break_limit=1000,
                 verbose = False
                 ):

        self.throttle = 0.0
        self.poll_delay = poll_delay
        self.running = True

        self._pi = None;
        self._triggerPin = trigger_pin
        self._echoPin = echo_pin
        self._sonarReader = None
        self._slowdown_limit = slowdown_limit
        self._break_limit = break_limit
        self.verbose = verbose
        self.distance = None

    def init(self):
        '''
        attempt to init gpio
        '''
        self._pi = pigpio.pi()
        self._sonarReader = SonarReader(self._pi, self._triggerPin, self._echoPin)
        return True


    def update(self):
        #wait for Tx to be online
        while self.running and not self.init():
            time.sleep(5)

        while self.running:
            self.distance = self._sonarReader.read()
            logger.info('sonar= {:01.2f}'.format(self.distance))
            if self.verbose:
                print('sonar= {:01.2f}'.format(self.distance))
            time.sleep(self.poll_delay)

    def run_threaded(self, throttle):
        if throttle < 0.1:
            return throttle
        #print('throttle={:01.2f}', throttle)
        if self.distance == None:
            return throttle
        if self.distance <= self._slowdown_limit:
            if self.distance <= self._break_limit:
                return -1
            else:
                return (throttle * (self.distance - self._break_limit))/(self._slowdown_limit - self._break_limit)
        return throttle

    def run(self, img_arr=None):
        raise Exception("We expect for this part to be run with the threaded=True argument.")

    def shutdown(self):
        self.running = False
        self._sonarReader.cancel()
        time.sleep(0.5)

