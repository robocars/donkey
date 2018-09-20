import time
import donkeycar as dk

import logging
logger = logging.getLogger('donkey.txaux')

class TxAuxCh(object):
    '''
    Battery Ctrl
    '''

    def __init__(self,
                 verbose = False
                 ):

        self.verbose = verbose
        self.user_mode = 'user'
        self.ch5 = False
        self.ch6 = False
        self.recording = False
        self.flag = ""

    def run_threaded(self):
        raise Exception("We expect for this part to be run with the threaded=False argument.")
        return False

    def run(self, user_mode, ch5, ch6, recording):
        self.recording = recording

        #ch6 is used to switch manual/autonomous driving
        if (ch6 != self.ch6):
            if (ch6 == True):
                logger.info('Ch6 - switch to On')
                logger.info('ChAux : Switch drive mode to local')
                self.user_mode = 'local'
            if (ch6 == False):
                logger.info('Ch6 - switch to Off')
                logger.info('ChAux : Switch drive mode to user')
                self.user_mode = 'user'
        if (ch5 != self.ch5):
                if (ch5 == True):
                    logger.info('Ch5 - switch to On')
                    if (self.user_mode == 'user'):
                        logger.info('ChAux - Switch Flag MK1 on')
                        self.flag = "MK1"
                    else:
                        logger.info('ChAux - switch recording to On')
                        self.recording = True
                if (ch5 == False):
                    logger.info('Ch5 - switch to Off')
                    if (self.user_mode == 'user'):
                        logger.info('ChAux - Switch Flag off')
                        self.flag = ""
                    else:
                        logger.info('ChAux - switch recording to Off')
                        self.recording = True

        self.ch5 = ch5
        self.ch6 = ch6
        return self.user_mode, self.flag, self.recording
    
    def shutdown(self):
        self.running = False
        time.sleep(0.5)

