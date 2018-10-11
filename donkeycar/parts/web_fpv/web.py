#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 24 20:10:44 2017

@author: wroscoe

remotes.py

The client and web server needed to control a car remotely. 
"""


import os
import simplejson as json
import time

import requests

import tornado.ioloop
import tornado.web
import tornado.gen
import tornado.iostream

import asyncio

from ... import utils

import logging
logger = logging.getLogger('donkey.web')



class FPVWebController(tornado.web.Application):

    def __init__(self):
        ''' 
        Create and publish variables needed on many of 
        the web handlers.
        '''

        print('Starting Donkey FPV Server...')

        this_dir = os.path.dirname(os.path.realpath(__file__))
        self.static_file_path = os.path.join(this_dir, 'templates', 'static')
        
        handlers = [
            (r"/", tornado.web.RedirectHandler, dict(url="/home")),
            (r"/home",Home),            
            (r"/video",VideoAPI),
            (r"/tele",TelemetrySource),
            (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": self.static_file_path}),
            ]

        settings = {'debug': True}
        self.teledata = {}
        super().__init__(handlers, **settings)

    def update(self, port=8887):
        ''' Start the tornado webserver. '''
        print(port)
        asyncio.set_event_loop(asyncio.new_event_loop())
        self.port = int(port)
        self.listen(self.port)
        tornado.ioloop.IOLoop.instance().start()
    
    def _run (self, img_arr=None, annoted_img=None, user_angle=None, user_throttle=None, user_mode=None, pilot_angle=None, pilot_throttle=None, throttle_boost=None, fullspeed=None):
        if (annoted_img is not None):
            self.img_arr = annoted_img
        else:
            self.img_arr = img_arr
        self.user_angle = user_angle
        self.user_throttle = user_throttle
        self.user_mode = user_mode
        self.pilot_angle = pilot_angle
        self.pilot_throttle = pilot_throttle
        self.throttle_boost = throttle_boost
        self.fullspeed = fullspeed
        if (user_mode == 'user'):
            self.teledata["user_angle"]  = self.user_angle 
            self.teledata["user_throttle"]  = self.user_throttle 
        else:
            if (self.pilot_angle != None):
                self.teledata["user_angle"]  =  self.pilot_angle.item() 
                self.teledata["user_throttle"]  = self.pilot_throttle.item()
        if (self.fullspeed != None):
            self.teledata["fullspeed"] = self.fullspeed.item() 

    def run_threaded(self, img_arr=None, annoted_img=None, user_angle=None, user_throttle=None, user_mode=None, pilot_angle=None, pilot_throttle=None, throttle_boost=None, fullspeed=None):
        self._run (img_arr, annoted_img, user_angle, user_throttle, user_mode, pilot_angle, pilot_throttle, throttle_boost, fullspeed)
        return 

    def run(self, img_arr=None, annoted_img=None, user_angle=None, user_throttle=None, user_mode=None, pilot_angle=None, pilot_throttle=None, throttle_boost=None, fullspeed=None):
        self._run (img_arr, annoted_img, user_angle, user_throttle, user_mode, pilot_angle, pilot_throttle, throttle_boost, fullspeed)
        return

        
class Home(tornado.web.RequestHandler):

    def get(self):
        data = {}
        self.render("templates/fpv.html", **data)
    

class VideoAPI(tornado.web.RequestHandler):
    '''
    Serves a MJPEG of the images posted from the vehicle. 
    '''
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        ioloop = tornado.ioloop.IOLoop.current()
        self.set_header("Content-type", "multipart/x-mixed-replace;boundary=--boundarydonotcross")

        self.served_image_timestamp = time.time()
        my_boundary = "--boundarydonotcross"
        while True:
            
            interval = .1
            if self.served_image_timestamp + interval < time.time():


                img = utils.arr_to_binary(self.application.img_arr)

                self.write(my_boundary)
                self.write("Content-type: image/jpeg\r\n")
                self.write("Content-length: %s\r\n\r\n" % len(img)) 
                self.write(img)
                self.served_image_timestamp = time.time()
                yield tornado.gen.Task(self.flush)
            else:
                yield tornado.gen.Task(ioloop.add_timeout, ioloop.time() + interval)

class TelemetrySource(tornado.web.RequestHandler):
    """Basic handler for server-sent events."""
    def initialize(self):
        """The ``source`` parameter is a string that is updated with
        new data. The :class:`EventSouce` instance will continuously
        check if it is updated and publish to clients when it is.
        """
        self.source= self.application
        self._last = None
        self.set_header('content-type', 'text/event-stream')
        self.set_header('cache-control', 'no-cache')

    @tornado.gen.coroutine
    def publish(self, data):
        """Pushes data to a listener."""
        try:
            self.write('data: {}\n\n'.format(data))
            yield self.flush()
        except tornado.iostream.StreamClosedError:
            print('tornado.iostream.StreamClosedError')
            pass

    @tornado.gen.coroutine
    def get(self):
        while True:
            yield self.publish(json.dumps(self.source.teledata, ensure_ascii=False, use_decimal=True))
            self._last = self.source.teledata
            yield tornado.gen.sleep(0.200)

