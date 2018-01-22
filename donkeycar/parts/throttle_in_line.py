#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wen Jan 22 2018

@author: bznoit.trinite

throttle_in_line.py


"""



import array
import time
import struct
from threading import Thread
import donkeycar as dk
from sys import platform
import logging
logger = logging.getLogger('donkey.tinline')

class ThrottleInLine(object):
    '''
    '''

    def __init__(self,
                 poll_delay=0,
                 verbose = False
                 ):

        self.poll_delay = poll_delay
        self.verbose = verbose
        self.throttle_boost = 1
        
    def init_throttle_in_line(self):
        return True
        '''
        '''


    def update(self):
        '''
        '''
        logger.info(".update")

    def run_threaded(self, img_arr=None):
        logger.info(".run_threaded")
        self.img_arr = img_arr
        return self.throttle_boost

    def run(self, img_arr=None):
        raise Exception("We expect for this part to be run with the threaded=True argument.")
        return False

    def shutdown(self):
        self.running = False
        time.sleep(0.5)

