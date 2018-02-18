#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 04 15:29:44 2018

@author: cristian.nitescu

test_remote.py


"""



import array
import time
import struct
from sys import platform

import pigpio

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

if __name__ == "__main__":
    
    import pigpio

    import test_remote;

    pi = pigpio.pi()

    pwm1 = test_remote.PWMReader(pi, 18);
    pwm2 = test_remote.PWMReader(pi, 23);
    pwm3 = test_remote.PWMReader(pi, 22);

    r = 1
    end = time.time() + 600;
    while time.time() < end:

        print("{} {} {} {} {} {} {}".format(r, pwm1.timeHigh, pwm1.timeLow, pwm2.timeHigh, pwm2.timeLow, pwm3.timeHigh, pwm3.timeLow))
        r += 1
        time.sleep(0.1)

    pwm1.cancel()
    pwm2.cancel()
    pwm3.cancel()

    pi.stop()
