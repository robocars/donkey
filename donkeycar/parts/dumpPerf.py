import time
from threading import Timer

import donkeycar as dk
from donkeycar.parts.configctrl import myConfig, CONFIG2LEVEL

import logging

class dumpPerf(object):
    '''
    Battery Ctrl
    '''

    def __init__(self
                 ):

        self.logger = logging.getLogger(myConfig['DEBUG']['PARTS']['PERFDUMP']['NAME'])
        self.logger.setLevel(myConfig['DEBUG']['PARTS']['PERFDUMP']['LEVEL'])
        self.dd = dk.perfmon.PerfReportManager()
        self.user_mode = 'user'
        self.dumpPerf()
 
    def run_threaded(self):
        raise Exception("We expect for this part to be run with the threaded=False argument.")
        return False

    def dumpPerf(self):
        self.timeout = myConfig['DEBUG']['PARTS']['PERFDUMP']['TIMEOUT']
        self.t = Timer(self.timeout, self.dumpPerf)
        self.t.start()
        self.dd.dumptAll("timeout "+self.user_mode)

    def resetPerf (self, reason):
        self.dd.dumptAll(reason)
        self.dd.resetPerf()

    def run(self, user_mode):

        if (self.user_mode != user_mode):
            self.resetPerf("switching to "+user_mode)
            self.user_mode = user_mode

        return 

    def shutdown(self):
        self.dd.dumptAll("Shuting down")
        time.sleep(0.5)

