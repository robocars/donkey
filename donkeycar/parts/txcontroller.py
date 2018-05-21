#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wen Dec 06 15:29:44 2017

@author: benoit.trinite

txwcontroller.py


"""



import array
import time
import struct
import os
from threading import Thread
import donkeycar as dk
from sys import platform

import logging
logger = logging.getLogger('donkey.txctrl')

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

class Txserial():
    '''
    An interface to a Tx through serial link
    '''
    counter = 0

    def __init__(self):
        self.ser = None
        self.lastLocalTs = 0
        self.lastDistTs = 0;

    def init(self):
        # Open serial link
        self.ser = serial.Serial(

               port='/dev/serial0',
               baudrate = 115200,
               parity=serial.PARITY_NONE,
               stopbits=serial.STOPBITS_ONE,
               bytesize=serial.EIGHTBITS,
               timeout=1
        )
        logger.info('/dev/serial0 initialized') 
        self.ser.writelines("init")       
        return True

    def poll(self, mode):
        '''
        query the state of the joystick, returns button which was pressed, if any,
        and axis which was moved, if any. button_state will be None, 1, or 0 if no changes,
        pressed, or released. axis_val will be a float from -1 to +1. button and axis will
        be the string label determined by the axis map in init.
        '''
         
        steering_tx = 1500
        throttle_tx = 0
        ch5_tx = 0
        ch6_tx = 0
        freq_tx = 60
        ts = 0
        msg=""

        if (Txserial.counter%10 == 0):
            self.ser.writelines(mode)       
        Txserial.counter += 1

        try:
            if self.ser.in_waiting > 50:
                logger.debug('poll: Serial buffer overrun {} ... flushing'.format(str(self.ser.in_waiting)))
                self.ser.reset_input_buffer()
            msg=self.ser.readline().decode('utf-8')
            ts, steering_tx, throttle_tx, ch5_tx, ch6_tx, freq_tx = map(int,msg.split(','))

        except:
            logger.debug('poll: Exception while parsing msg')

        now=time.clock()*1000
        logger.debug('poll: {} {}'.format(msg.strip(),len(msg)))
        if (steering_tx == -1):
            logger.debug('poll: No Rx signal , forcing idle position')
            return 0,1500,0,0,60
        if (ts-self.lastDistTs < 2*(now-self.lastLocalTs)):
            logger.debug('poll: underun dist {} local {}'.format(ts-self.lastDistTs, now-self.lastLocalTs))
        self.lastLocalTs = now
        self.lastDistTs = ts
        logger.debug('poll: ts {} steering_tx= {:05.0f} throttle_tx= {:05.0f} freq_tx= {:02.0f}'.format(ts, steering_tx, throttle_tx, freq_tx))


        return throttle_tx, steering_tx, ch5_tx, ch6_tx, freq_tx


class TxController(object):
    '''
    Tx client using access to local serial input
    '''

    def __init__(self, poll_delay=0.0,
                 throttle_tx_min=913,
                 throttle_tx_max=2111,
                 steering_tx_min=955,
                 steering_tx_max=2085,
                 throttle_tx_thresh=1520,
                 ch_aux_tx_thresh=1500,
                 auto_record_on_throttle=True,
                 verbose = False
                 ):

        self.angle = 0.0
        self.throttle = 0.0
        self.mode = 'user'
        self.poll_delay = poll_delay
        self.running = True
        self.throttle_tx_thresh = throttle_tx_thresh
        self.ch_aux_tx_thresh = ch_aux_tx_thresh
        self.throttle_tx_min = throttle_tx_min
        self.throttle_tx_max = throttle_tx_max
        self.steering_tx_min = steering_tx_min
        self.steering_tx_max = steering_tx_max

        self.ch5 = False
        self.ch6 = False
        self.last_ch5 = False
        self.last_ch6 = False
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
            throttle_tx, steering_tx, ch5_tx, ch6_tx, freq_tx = self.tx.poll(self.mode)
            if throttle_tx > self.throttle_tx_thresh:
                self.throttle = map_range(throttle_tx, self.throttle_tx_min, self.throttle_tx_max, -1, 1)
            else:
                self.throttle = 0
            self.on_throttle_changes()
            self.angle = 0-map_range(steering_tx, self.steering_tx_min, self.steering_tx_max, -1, 1)

            if (ch5_tx > self.ch_aux_tx_thresh+100):
                self.ch5 = True

            if (ch5_tx < self.ch_aux_tx_thresh-100):
                self.ch5 = False

            if (ch6_tx > self.ch_aux_tx_thresh+100):
                self.ch6 = True

            if (ch6_tx < self.ch_aux_tx_thresh-100):
                self.ch6 = False
    
            if (self.ch5 != self.last_ch5):
                if (self.ch5 == True):
                    logger.info('Ch5 - switch to On')
                    logger.info('ChAux : Switch drive mode to local')
                    self.mode = 'local'
                if (self.ch5 == False):
                    logger.info('Ch5 - switch to Off')
                    logger.info('ChAux : Switch drive mode to user')
                    self.mode = 'user'
            if (self.ch6 != self.last_ch6):
                if (self.ch6 == True):
                    logger.info('Ch6 - switch to On')
                    logger.info('ChAux : exit()')
                    os._exit(1)
                if (self.ch6 == False):
                    logger.info('Ch6 - switch to Off')
                
            self.last_ch5 = self.ch5
            self.last_ch6 = self.ch6

            logger.debug('angle= {:01.2f} throttle= {:01.2f}'.format (self.angle, self.throttle))
            time.sleep(self.poll_delay)

    def run_threaded(self, img_arr=None, annoted_img=None):
        if (annoted_img is not None):
            self.img_arr = annoted_img
        else:
            self.img_arr = img_arr
        return self.angle, self.throttle, self.mode, self.recording

    def run(self, img_arr=None, img_annoted=None):
        raise Exception("We expect for this part to be run with the threaded=True argument.")
        return False

    def shutdown(self):
        self.running = False
        time.sleep(0.5)

