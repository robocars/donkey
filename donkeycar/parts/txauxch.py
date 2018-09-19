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
        self.flag = ""

    def run_threaded(self):
        raise Exception("We expect for this part to be run with the threaded=False argument.")
        return False

    def run(self, user_mode, ch5, ch6):
        #ch6 is used to switch manual/autonomous driving
        if (ch6 != self.ch6):
            if (ch6 == True):
                logger.info('Ch6 - switch to On')
                logger.info('ChAux : Switch drive mode to local')
                self.mode = 'local'
            if (ch6 == False):
                logger.info('Ch6 - switch to Off')
                logger.info('ChAux : Switch drive mode to user')
                self.mode = 'user'
        if (ch5 != self.ch5):
                if (ch5 == True):
                    logger.info('Ch5 - switch to On')
                    if (self.mode == 'user'):
                        logger.info('ChAux : exit()')
                        self.tx.ledStatus('init')
                        time.sleep(0.2)
                        os._exit(1)
                    else:
                        self.flag = "MK1"
                if (ch5 == False):
                    logger.info('Ch5 - switch to Off')
                    if (self.mode == 'user'):
                        logger.info('No Aux action for that !')
                    else:
                        self.flag = ""

        self.ch5 = ch5
        self.ch6 = ch6
        return self.user_mode, self.flag):
    
    def shutdown(self):
        self.running = False
        time.sleep(0.5)

