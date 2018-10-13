import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import yaml
import os
import copy

import logging
logger = logging.getLogger('donkey.dynconfig')

myConfig = {}

class Watcher:
    def __init__(self, configPath, eventHandler):
        self.configPath = configPath
        self.eventHandler = eventHandler
        self.observer = Observer()

    def run(self):
        self.observer.schedule(self.eventHandler, self.configPath, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(5)
        except:
            self.observer.stop()
            logger.info("Error")

        self.observer.join()


class ConfigFile(FileSystemEventHandler):
    def __init__ (self, configPath):
        self.configPath = configPath
        self.cfg = []

    def reload(self):
        global myConfig
        with open(os.path.join (self.configPath, "config.yaml"), 'r') as ymlfile:
            myConfig.update(yaml.load(ymlfile))
            for section in myConfig:
                logger.info("Section found :"+section)

    def on_any_event(self, event):
        if event.is_directory:
            return None

        elif event.event_type == 'created':
            # Take any action here when a file is first created.
            logger.info ("Received created event - %s." % event.src_path)

        elif event.event_type == 'modified':
            # Taken any action here when a file is modified.
            logger.info ("Received modified event - %s." % event.src_path)
            if (event.src_path == os.path.join (self.configPath, "config.yaml")):
                logger.info ("Reload configuration")
                self.reload()



class ConfigController(object):
    '''
    Config Ctrl
    '''

    def __init__(self, configPath, 
                 verbose = False
                 ):

        self.verbose = verbose
        self.configPath = configPath
        self.c = ConfigFile (self.configPath)
        self.event_handler = self.c
        self.c.reload()
        self.w = Watcher(self.configPath, self.event_handler)
        
    def run_threaded(self):
        return

    def update(self):
        self.w.run()


    def run(self):
        raise Exception("We expect for this part to be run with the threaded=True argument.")
        return False
    
    def shutdown(self):
        self.running = False
        time.sleep(0.5)


