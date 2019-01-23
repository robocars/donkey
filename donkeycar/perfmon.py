import time
import operator
import logging
from threading import get_ident, current_thread

from donkeycar.parts.configctrl import myConfig, CONFIG2LEVEL

from ascii_graph import Pyasciigraph

distriDuration = {}
distriCycle = {}
timeline = []

def timelineAddEvent (tag, state):
    global timeline
    evt={}
    ts = int(round(time.time() * 1000))
    evt['ts']=ts
    evt['thread']=current_thread().name
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

def LogEvent(tag):
    timelineAddEvent(tag, 'evt')

class TaskDuration:
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

class TaskCycle:
    def __init__(self, tag):
        self.tag = tag
        self.last = None

    def LogCycle(self):
        ts = time.time()
        if (self.last != None):
            cycle = round((ts-self.last)*1000)
            if not (keys_exists(distriCycle, self.tag)):
                distriCycle[self.tag]={}
            if keys_exists(distriCycle, self.tag, cycle):
                distriCycle[self.tag][cycle]+=1
            else:
                distriCycle[self.tag][cycle]=1
        self.last = ts
        return self

class PerfReportManager:
    def __init__(self):
        self.init=True
        self.logger = logging.getLogger(myConfig['DEBUG']['PARTS']['PERFMON']['NAME'])
        self.logger.setLevel(CONFIG2LEVEL[myConfig['DEBUG']['PARTS']['PERFMON']['LEVEL']])

    
    def getSortedDuration(self, tag):
            return (sorted(distriDuration[tag].items(), key=lambda kv: kv[0]))

    def getSortedCycle(self, tag):
            return (sorted(distriCycle[tag].items(), key=lambda kv: kv[0]))

    def dumptAll(self, context=""):
        global distriDuration
        self.logger.info("Dump all perfmon recorded timings")
        with  open(myConfig['DEBUG']['PARTS']['PERFMON']['FILE'], "a+") as myfile:
            for part in distriDuration:
                sorted_distriDuration = self.getSortedDuration(part)
                #self.logger.info('Timing for parts :'+part)
                #self.logger.info (sorted_distriDuration)
                graph = Pyasciigraph(graphsymbol='#')
                myfile.write("----------------------- {}\n".format(context))
                myfile.write("Duration Timing for parts : {}\n".format(part))
                for line in  graph.graph(part, sorted_distriDuration):
                    myfile.write("{}\n".format(line.encode('ascii','ignore').decode('utf-8')))
                #self.logger.info(line.encode('ascii','ignore').decode('utf-8'))
            for part in distriCycle:
                sorted_distriCycle = self.getSortedCycle(part)
                graph = Pyasciigraph(graphsymbol='#')
                myfile.write("----------------------- {}\n".format(context))
                myfile.write("Cycle Timing for parts : {}\n".format(part))
                for line in  graph.graph(part, sorted_distriCycle):
                    myfile.write("{}\n".format(line.encode('ascii','ignore').decode('utf-8')))
        myfile.close()
        with  open(myConfig['DEBUG']['PARTS']['TRACER']['FILE'], "a+") as myfile:
            myfile.write("----------------------- {}\n".format(context))
            for evt in  timeline:
                myfile.write("{0} {1} {2} {3}\n".format(evt['ts'], evt['thread'], evt['tag'], evt['state']))
            myfile.close()

    def resetPerf(self):
        global distriDuration
        global timeline
        distriDuration = {}
        distriCycle = {}
        timeline = []

    
