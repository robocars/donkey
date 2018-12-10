import time
import operator
import logging

from donkeycar.parts.configctrl import myConfig, CONFIG2LEVEL

from ascii_graph import Pyasciigraph

distriDuration = {}
timeline = []

def timelineAddEvent (tag, state):
    global timeline
    evt={}
    ts = int(round(time.time() * 1000))
    evt['ts']=ts
    evt['tag']=tag
    evt['state']=state
    timeline.append(evt)
    if (len(timeline) > 3000):
        timeline.pop(0)
def keys_exists(element, *keys):
    '''
    Check if *keys (nested) exists in `element` (dict).
    '''
    if type(element) is not dict:
        raise AttributeError('keys_exists() expects dict as first argument.')
    if len(keys) == 0:
        raise AttributeError('keys_exists() expects at least two arguments, one given.')

    _element = element
    for key in keys:
        try:
            _element = _element[key]
        except KeyError:
            return False
    return True

class MeasureDuration:
    def __init__(self, tag):
        self.tag = tag
        self.start = None

    def __enter__(self):
        self.start = time.time()
        timelineAddEvent(self.tag, 'enter')
        return self
 
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = int((time.time() - self.start) * 1000)
        timelineAddEvent(self.tag, 'leave')
        if not (keys_exists(distriDuration, self.tag)):
            distriDuration[self.tag]={}

        if keys_exists(distriDuration, self.tag, duration):
            distriDuration[self.tag][duration]+=1
        else:
            distriDuration[self.tag][duration]=1
            #distri[self.tag]['max']=duration
        #newmax = max(distri[self.tag]['max'], duration)
        #distri[self.tag]['max']=newmax

class PerfReportManager:
    def __init__(self):
        self.init=True
        self.logger = logging.getLogger(myConfig['DEBUG']['PARTS']['PERFMON']['NAME'])
        self.logger.setLevel(CONFIG2LEVEL[myConfig['DEBUG']['PARTS']['PERFMON']['LEVEL']])

    
    def getSorted(self, tag):
            return (sorted(distriDuration[tag].items(), key=lambda kv: kv[0]))

    def dumptAll(self):
        print("Dump all perfmon recorded timings :")
        for part in distriDuration:
            sorted_distriDuration = self.getSorted(part)
            print('Timing for parts :'+part)
            #self.logger.info (sorted_distriDuration)
            graph = Pyasciigraph()
            with open(myConfig['DEBUG']['PARTS']['PERFMON']['FILE'], "w+") as myfile:
                for line in  graph.graph(part, sorted_distriDuration):
                    myfile.write(line)
            myfile.close()
    
