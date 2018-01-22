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

import numpy as np
import cv2

from threading import Thread
import donkeycar as dk
from sys import platform
import logging
logger = logging.getLogger('donkey.tinline')

def region_of_interest(img, vertices):
    """
    Applies an image mask.
    Only keeps the region of the image defined by the polygon
    formed from `vertices`. The rest of the image is set to black.
    """
    #defining a blank mask to start with
    mask = np.zeros_like(img)

    #defining a 3 channel or 1 channel color to fill the mask with depending on the input image
    if len(img.shape) > 2:
        channel_count = img.shape[2]  # i.e. 3 or 4 depending on your image
        ignore_mask_color = (255,) * channel_count
    else:
        ignore_mask_color = 255

    #filling pixels inside the polygon defined by "vertices" with the fill color
    cv2.fillPoly(mask, vertices, ignore_mask_color)

    #returning the image only where mask pixels are nonzero
    masked_image = cv2.bitwise_and(img, mask)
    return masked_image

def hough_lines(img, rho, theta, threshold, min_line_len, max_line_gap):
    """
    `img` should be the output of a Canny transform.
        
    Returns an image with hough lines drawn.
    """
    lines = cv2.HoughLinesP(img, rho, theta, threshold, np.array([]), minLineLength=min_line_len, maxLineGap=max_line_gap)
    return lines

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
        self.running = True

        
    def init_throttle_in_line(self):
        return True
        '''
        '''


    def update(self):
        '''
        '''
        logger.info(".update")
        while self.running and not self.init_tx():
            time.sleep(5)

        while self.running:
            gray_image = cv2.cvtColor(self.img_arr, cv2.COLOR_RGB2GRAY)
            hsv_image = cv2.cvtColor(self.img_arr, cv2.COLOR_RGB2HSV)
            ilower_yellow = np.array([20, 100, 100], dtype = "uint8")
            upper_yellow = np.array([30, 255, 255], dtype="uint8")
            mask_yellow = cv2.inRange(hsv_image, lower_yellow, upper_yellow)
            mask_white = cv2.inRange(gray_image, 200, 255)
            mask_yw = cv2.bitwise_or(mask_white, mask_yellow)
            mask_yw_image = cv2.bitwise_and(gray_image, mask_yw)

            kernel_size = 5
            gauss_gray = cv2.gaussian_blur(mask_yw_image,kernel_size)

            low_threshold = 50
            high_threshold = 150
            canny_edges = cv2.canny(gauss_gray,low_threshold,high_threshold)

            imshape = self.img_arr.shape
            lower_left = [imshape[1]/9,imshape[0]]
            lower_right = [imshape[1]-imshape[1]/9,imshape[0]]
            top_left = [imshape[1]/2-imshape[1]/8,imshape[0]/2+imshape[0]/10]
            top_right = [imshape[1]/2+imshape[1]/8,imshape[0]/2+imshape[0]/10]
            vertices = [np.array([lower_left,top_left,top_right,lower_right],dtype=np.int32)]
            
            roi_image = region_of_interest(canny_edges, vertices)
            #rho and theta are the distance and angular resolution of the grid in Hough space
            #same values as quiz
            rho = 4
            theta = np.pi/180
            #threshold is minimum number of intersections in a grid for candidate line to go to output
            threshold = 30
            min_line_len = 100
            max_line_gap = 180
            #my hough values started closer to the values in the quiz, but got bumped up considerably for the challenge video
            lines = hough_lines(roi_image, rho, theta, threshold, min_line_len, max_line_gap)

            for rho,theta in lines[0]:
                logger.info('rho= {:01.5f} theta= {:01.5f}'.format (rho, theta))
            time.sleep(self.poll_delay)


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

