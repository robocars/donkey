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
import math

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

def draw_lines(img, lines, color=[255, 0, 0], thickness=2):
    """
    NOTE: this is the function you might want to use as a starting point once you want to
    average/extrapolate the line segments you detect to map out the full
    extent of the lane (going from the result shown in raw-lines-example.mp4
    to that shown in P1_example.mp4).
    Think about things like separating line segments by their
    slope ((y2-y1)/(x2-x1)) to decide which segments are part of the left
    line vs. the right line.  Then, you can average the position of each of
    the lines and extrapolate to the top and bottom of the lane.
    This function draws `lines` with `color` and `thickness`.
    Lines are drawn on the image inplace (mutates the image).
    If you want to make the lines semi-transparent, think about combining
    this function with the weighted_img() function below
    """
    for line in lines:
        for x1,y1,x2,y2 in line:
            cv2.line(img, (x1, y1), (x2, y2), color, thickness)

def hough_lines(img, rho, theta, threshold, min_line_len, max_line_gap):
    """
    `img` should be the output of a Canny transform.
        
    Returns an image with hough lines drawn.
    """
    lines = cv2.HoughLinesP(img, rho, theta, threshold, np.array([]), minLineLength=min_line_len, maxLineGap=max_line_gap)
    return lines

def gaussian_blur(img, kernel_size):
    """Applies a Gaussian Noise kernel"""
    return cv2.GaussianBlur(img, (kernel_size, kernel_size), 0)

def canny(img, low_threshold, high_threshold):
    """Applies the Canny transform"""
    #imgCopy = np.uint8(img)
    return cv2.Canny(img, low_threshold, high_threshold)

def weighted_img(img, initial_img, α=0.8, β=1., λ=0.):
    """
    `img` is the output of the hough_lines(), An image with lines drawn on it.
    Should be a blank image (all black) with lines drawn on it.
    `initial_img` should be the image before any processing.
    The result image is computed as follows:
    initial_img * α + img * β + λ
    NOTE: initial_img and img must be the same shape!
    """
    return cv2.addWeighted(initial_img, α, img, β, λ)

def GetAngleOfLineBetweenTwoPoints(x1, y1,x2,y2):
    xDiff = x2 - x1
    yDiff = y2 - y1
    return math.degrees(math.atan2(yDiff, xDiff))

def detectBoostCondition(img, angle_min, angle_max):

    annoted_img = img
    img2=np.uint8(img)
    gray_image = cv2.cvtColor(img2, cv2.COLOR_RGB2GRAY)
    hsv_image = cv2.cvtColor(img2, cv2.COLOR_RGB2HSV)
    lower_yellow = np.array([20, 100, 100], dtype = "uint8")
    upper_yellow = np.array([30, 255, 255], dtype="uint8")
    mask_yellow = cv2.inRange(hsv_image, lower_yellow, upper_yellow)
    mask_white = cv2.inRange(gray_image, 200, 255)
    mask_yw = cv2.bitwise_or(mask_white, mask_yellow)
    mask_yw_image = cv2.bitwise_and(gray_image, gray_image, mask_yw)


    kernel_size = 5
    gauss_gray = gaussian_blur(mask_yw_image,kernel_size)

    low_threshold = 50
    high_threshold = 150
    canny_edges = canny(gauss_gray,low_threshold,high_threshold)

    imshape = img2.shape
    lower_left = [0,90]
    lower_right = [160,90]
    top_left = [0,20]
    top_right = [160,20]
    vertices = [np.array([lower_left,top_left,top_right,lower_right],dtype=np.int32)]

    roi_image = region_of_interest(canny_edges, vertices)
    #rho and theta are the distance and angular resolution of the grid in Hough space
    #same values as quiz
    rho = 1
    theta = np.pi/45
    #threshold is minimum number of intersections in a grid for candidate line to go to output
    threshold = 30
    min_line_len = 40
    max_line_gap = 180
    #my hough values started closer to the values in the quiz, but got bumped up considerably for the challenge video
    lines = cv2.HoughLinesP(roi_image, rho, theta, threshold, np.array([]), minLineLength=min_line_len, maxLineGap=max_line_gap)
    if lines is not None:
        line_img = np.zeros((img2.shape[0], img2.shape[1], 3), dtype=np.uint8)
        draw_lines(line_img, lines)
        annoted_img = weighted_img(line_img, img2, α=0.8, β=1., λ=0.)
        angle1=False
        angle2=False
        for idx, line in enumerate(lines):
            angle = GetAngleOfLineBetweenTwoPoints(line[0][0],line[0][1],line[0][2],line[0][3])
            #print(d[4]+" "+str(idx)+" "+str(angle))
            if (angle < angle_max and angle > angle_min):
                angle1=True
            if (angle > -angle_max and angle <-angle_min):
                angle2=True
            if (angle < angle_min and angle > -angle_min):
                angle1=False
                angle2=False
            if (angle > angle_max or angle < -angle_max):
                angle1=False
                angle2=False                
        return angle1 and angle2, annoted_img
    return False, annoted_img

class ThrottleInLine(object):
    '''
    '''

    def __init__(self,
                 angle_min=30,
                 angle_max=95,
                 poll_delay=0,
                 verbose = False
                 ):

        self.poll_delay = poll_delay
        self.angle_min = angle_min
        self.angle_max = angle_max
        self.verbose = verbose
        self.throttle_boost = False
        self.running = True
        self.img_arr = None
        self.annoted_img = None

    def update(self):
        '''
        '''
        while self.running:
            self.throttle_boost = False
            if (self.img_arr is not None):
                self.throttle_boost, self.annoted_img = detectBoostCondition(self.img_arr, self.angle_min,self.angle_max)
            time.sleep(self.poll_delay)

    def run_threaded(self, img_arr=None):
        self.img_arr = img_arr
        return self.throttle_boost, self.annoted_img

    def run(self, img_arr=None):
        raise Exception("We expect for this part to be run with the threaded=True argument.")
        return False

    def shutdown(self):
        self.running = False
        time.sleep(0.5)

