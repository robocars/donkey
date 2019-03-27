import os
import time
import numpy as np
from PIL import Image
import glob
import cv2

import donkeycar as dk
import subprocess

from donkeycar.parts.configctrl import myConfig, CONFIG2LEVEL

import logging

class BaseCamera:

    def run_threaded(self):
        return self.frame

class PiCamera(BaseCamera):
    def __init__(self, resolution=(120, 160), framerate=20):

        self.logger = logging.getLogger(myConfig['DEBUG']['PARTS']['CAMERA']['NAME'])
        self.logger.setLevel(myConfig['DEBUG']['PARTS']['CAMERA']['LEVEL'])

        from picamera.array import PiRGBArray
        from picamera import PiCamera
        resolution = (resolution[1], resolution[0])
        # initialize the camera and stream
        self.camera = PiCamera() #PiCamera gets resolution (height, width)
        self.camera.resolution = resolution
        self.camera.framerate = framerate

        #self.camera.exposure_mode = 'sports'
        #self.camera.iso = 800
        self.rawCapture = PiRGBArray(self.camera, size=resolution)
        self.stream = self.camera.capture_continuous(self.rawCapture,
            format="rgb", use_video_port=True)

        # initialize the frame and the variable used to indicate
        # if the thread should be stopped
        self.frame = None
        self.on = True

        self.logger.info('PiCamera loaded.. .warming camera')
        time.sleep(2)


    def run(self):
        with dk.perfmon.TaskDuration('RaspiCam') as m:
            f = next(self.stream)
        frame = f.array
        self.rawCapture.truncate(0)
        return frame

    def update(self):
        # keep looping infinitely until the thread is stopped
        for f in self.stream:
            # grab the frame from the stream and clear the stream in
            # preparation for the next frame
            self.frame = f.array
            self.rawCapture.truncate(0)

            # if the thread indicator variable is set, stop the thread
            if not self.on:
                break

    def shutdown(self):
        # indicate that the thread should be stopped
        self.on = False
        self.logger.info('stoping PiCamera')
        time.sleep(.5)
        self.stream.close()
        self.rawCapture.close()
        self.camera.close()

class Webcam(BaseCamera):
    def init_cam (self, resolution = (160, 120), fps=60):
        
        self.logger = logging.getLogger(myConfig['DEBUG']['PARTS']['CAMERA']['NAME'])
        self.logger.setLevel(CONFIG2LEVEL[myConfig['DEBUG']['PARTS']['CAMERA']['LEVEL']])

        self.cam = cv2.VideoCapture(0+cv2.CAP_V4L2)
        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH,resolution[1])
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT,resolution[0])
        self.cam.set(cv2.CAP_PROP_FPS, fps)
        
        self.resolution = resolution
        self.fps = fps

    def __init__(self, resolution = (160, 120), fps=60, framerate = 20):

        super().__init__()

        self.init_cam(resolution, fps)
        self.framerate = framerate

        # initialize variable used to indicate
        # if the thread should be stopped
        self.frame = None
        self.on = True
        self.perflogger = dk.perfmon.TaskCycle('WebCam')
        self.logger.info('WebcamVideoStream loaded.. .warming camera')

        time.sleep(2)
        check_fps = self.cam.get(cv2.CAP_PROP_FPS)
        if (check_fps == 0):
            self.cam.release()
            self.logger.info('WebcamVideoStream loaded.. .Error, busy, retstarting')
            os._exit(1)
            time.sleep(2)

        if (myConfig['CAMERA']['AUTO_EXP'] == 1):
            subprocess.run(["v4l2-ctl", "-d /dev/video0 -c exposure_auto=3"])             
            self.logger.info('Exp mode : auto')
        else:
            subprocess.run(["v4l2-ctl", "-d /dev/video0 -c exposure_auto=1"])
            time.sleep(2)             
            subprocess.run(["v4l2-ctl", "-d /dev/video0 -c exposure_absolute="+str(myConfig['CAMERA']['EXP'])])             
            self.logger.info('Exp mode : manual ('+str(myConfig['CAMERA']['EXP'])+')')

        check_fps = self.cam.get(cv2.CAP_PROP_FPS)
        self.logger.info("Camera read configuration:")
        self.logger.info("Camera Width :"+str(self.cam.get(cv2.CAP_PROP_FRAME_WIDTH)))
        self.logger.info("Camera Height :"+str(self.cam.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        self.logger.info("Camera FPS :"+str(check_fps))
        self.logger.info("Camera backend :"+str(self.cam.get(cv2.CAP_PROP_MODE)))
        self.logger.info("Camera Exp :"+str(self.cam.get(cv2.CAP_PROP_EXPOSURE)))
        self.logger.info("Camera Auto Exp :"+str(self.cam.get(cv2.CAP_PROP_AUTO_EXPOSURE)))

    def update(self):
        from datetime import datetime, timedelta

        while self.on:
            start = datetime.now()

            with dk.perfmon.TaskDuration('WebCam') as m:
                self.perflogger.LogCycle()
                ret, snapshot = self.cam.read()
            self.logger.debug("New image acquired")
            if ret:
                self.frame = cv2.cvtColor(snapshot, cv2.COLOR_BGR2RGB)
                # We don't need anymore this resizing, we configure the right resolution in the WebCam
                #self.frame = cv2.resize(snapshot1,(160,120), interpolation = cv2.INTER_AREA)

            stop = datetime.now()
            s = 1 / self.framerate - (stop - start).total_seconds()
            if s > 0:
                time.sleep(s)

        self.cam.release()

    def run_threaded(self):
        dk.perfmon.LogEvent('WebCam-Poll')
        return self.frame

    def shutdown(self):
        # indicate that the thread should be stopped
        self.on = False
        self.logger.info('stoping Webcam')
        time.sleep(.5)

class MockCamera(BaseCamera):
    '''
    Fake camera. Returns only a single static frame
    '''
    def __init__(self, resolution=(160, 120), image=None):
        if image is not None:
            self.frame = image
        else:
            self.frame = Image.new('RGB', resolution)

    def update(self):
        pass

    def shutdown(self):
        pass

class ImageListCamera(BaseCamera):
    '''
    Use the images from a tub as a fake camera output
    '''
    def __init__(self, path_mask='~/d2/data/**/*.jpg'):
        self.image_filenames = glob.glob(os.path.expanduser(path_mask), recursive=True)
    
        def get_image_index(fnm):
            sl = os.path.basename(fnm).split('_')
            return int(sl[0])

        '''
        I feel like sorting by modified time is almost always
        what you want. but if you tared and moved your data around,
        sometimes it doesn't preserve a nice modified time.
        so, sorting by image index works better, but only with one path.
        '''
        self.image_filenames.sort(key=get_image_index)
        #self.image_filenames.sort(key=os.path.getmtime)
        self.num_images = len(self.image_filenames)
        logger.info('%d images loaded.' % self.num_images)
        logger.info( self.image_filenames[:10])
        self.i_frame = 0
        self.frame = None
        self.update()

    def update(self):
        pass

    def run_threaded(self):        
        if self.num_images > 0:
            self.i_frame = (self.i_frame + 1) % self.num_images
            self.frame = Image.open(self.image_filenames[self.i_frame]) 

        return np.asarray(self.frame)

    def shutdown(self):
        pass
