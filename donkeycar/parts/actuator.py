"""
actuators.py
Classes to control the motors and servos. These classes 
are wrapped in a mixer class before being used in the drive loop.
"""

import time

import donkeycar as dk

from donkeycar.parts.configctrl import myConfig

import logging
logger = logging.getLogger('donkey.actuator')

class PCA9685:
    ''' 
    PWM motor controler using PCA9685 boards. 
    This is used for most RC Cars
    '''
    def __init__(self, channel, frequency=60):
        import Adafruit_PCA9685
        # Initialise the PCA9685 using the default address (0x40).
        self.pwm = Adafruit_PCA9685.PCA9685()
        self.pwm.set_pwm_freq(frequency)
        self.channel = channel

    def set_pulse(self, pulse):
        self.pwm.set_pwm(self.channel, 0, pulse) 

    def run(self, pulse):
        self.set_pulse(pulse)
        
class PWMSteering:
    """
    Wrapper over a PWM motor cotnroller to convert angles to PWM pulses.
    """
    LEFT_ANGLE = -1 
    RIGHT_ANGLE = 1

    def __init__(self, controller=None,
                       left_pulse=290,
                       right_pulse=490):

        self.controller = controller
        self.left_pulse = left_pulse
        self.right_pulse = right_pulse

    def run(self, angle):
        #map absolute angle to angle that vehicle can implement.
        logger.debug('Output angle order= {:01.2f}'.format(angle))
        pulse = dk.utils.map_range(angle,
                                self.LEFT_ANGLE, self.RIGHT_ANGLE,
                                self.left_pulse, self.right_pulse)
#        print ("PWMSteering pulse="+str(pulse))
        logger.debug('Output angle pulse= {:03.0f}'.format(pulse))
        self.controller.set_pulse(pulse)

    def shutdown(self):
        self.run(0) #set steering straight



class PWMThrottle:
    """
    Wrapper over a PWM motor cotnroller to convert -1 to 1 throttle
    values to PWM pulses.
    """
    MIN_THROTTLE = -1
    MAX_THROTTLE =  1

    def __init__(self, controller=None):

        self.mode = "user"
        self.kick = []
        #send zero pulse to calibrate ESC
        self.controller = controller
        self.controller.set_pulse(myConfig['ACTUATOR']['THROTTLE_STOPPED_PWM'])
        self.fullspeed_hysteresis = 0
        self.brake_hysteresis = 0
        time.sleep(1)

    def reloadKick(self):
        self.kick = [myConfig['ACTUATOR']['THROTTLE_KICK_PULSE']]*myConfig['ACTUATOR']['THROTTLE_KICK_LENGTH']
        logger.debug('Kicker reloaded')

    def run(self, throttle, mode=None, fullspeed=None, brake=None):

        global myConfig

        if self.mode == "user" and mode != "user":
            self.reloadKick()

        if (self.mode != "user" and mode == "user"):
            self.brake_hysteresis = myConfig['ACTUATOR']['FULLSPEED_HYSTERESIS_LENGTH']

        self.mode = mode

        if (fullspeed==None):
            fullspeed = 0
        if (brake==None):
            brake=0
            
        logger.debug('throttle order= {:01.2f}'.format(throttle))

        if ((throttle > 0) or (self.mode != "user")):
            #Forward direction
            pulse = dk.utils.map_range(throttle,
                                    0, self.MAX_THROTTLE, 
                                    myConfig['ACTUATOR']['THROTTLE_STOPPED_PWM'], myConfig['ACTUATOR']['THROTTLE_FORWARD_PWM'])
            if (self.mode != "user"):
                # Autonomous mode
                if (myConfig['ACTUATOR']['THROTTLE_CONSTANT_MODE'] == 1):
                    # If constant mode, just apply always kick  as nominal value 
                    logger.debug('constant speed mode : fullspeed prediction = '+str(fullspeed) + ' brake_decision = '+str(brake))
                    if (brake > myConfig['ACTUATOR']['BRAKE_DECISION_THRESH']):
                        logger.debug('constant speed mode : brake')
                        self.brake_hysteresis = myConfig['ACTUATOR']['FULLSPEED_HYSTERESIS_LENGTH']
                    elif (fullspeed > myConfig['ACTUATOR']['FULLSPEED_DECISION_THRESH']):
                        logger.debug('constant speed mode : fullspeed')
                        self.fullspeed_hysteresis = myConfig['ACTUATOR']['FULLSPEED_HYSTERESIS_LENGTH']
                    else:
                        logger.debug('constant speed mode : regular speed')
                        pulse = myConfig['ACTUATOR']['THROTTLE_KICK_PULSE']
                else:
                    # Not in constant mode, Ensure thottle order would not go below a limit (risk of motor shutdown)
                    if pulse < myConfig['ACTUATOR']['THROTTLE_MIN_SPD_PULSE']:
                        logger.debug('PWMThrottle order too low')
                        pulse = myConfig['ACTUATOR']['THROTTLE_MIN_SPD_PULSE']

                # Motor cann not start at too low throttle, kick it for the first cycles             
                if (len(self.kick)>0):
                    logger.debug('Kicker active')
                    pulse = self.kick.pop()

        else:
            #reverse direction in manual mode
            pulse = dk.utils.map_range(throttle,
                                    self.MIN_THROTTLE, 0, 
                                    myConfig['ACTUATOR']['THROTTLE_REVERSE_PWM'], myConfig['ACTUATOR']['THROTTLE_STOPPED_PWM'])

        if (self.brake_hysteresis>0):
            logger.debug('Apply brake for next '+str(self.brake_hysteresis-1)+' cycle')
            pulse = myConfig['ACTUATOR']['THROTTLE_BRAKE_PULSE']
            self.brake_hysteresis -= 1
            if (self.brake_hysteresis == 0):
                self.reloadKick()
            
        if (self.fullspeed_hysteresis>0):
            logger.debug('Appluy fullspeed for next '+str(self.fullspeed_hysteresis-1)+' cycle')
            pulse = myConfig['ACTUATOR']['THROTTLE_FULLSPEED_PULSE']
            self.fullspeed_hysteresis -= 1

        logger.debug('Output throttle pulse= {:03.0f}'.format(pulse))
        self.controller.set_pulse(pulse)
        
    def shutdown(self):
        self.controller.set_pulse(0) #stop vehicle

    def gracefull_shutdown(self):
        self.controller.set_pulse(0) #stop vehicle




class Adafruit_DCMotor_Hat:
    ''' 
    Adafruit DC Motor Controller 
    Used for each motor on a differential drive car.
    '''
    def __init__(self, motor_num):
        from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor
        import atexit
        
        self.FORWARD = Adafruit_MotorHAT.FORWARD
        self.BACKWARD = Adafruit_MotorHAT.BACKWARD
        self.mh = Adafruit_MotorHAT(addr=0x60) 
        
        self.motor = self.mh.getMotor(motor_num)
        self.motor_num = motor_num
        
        atexit.register(self.turn_off_motors)
        self.speed = 0
        self.throttle = 0
    
        
    def run(self, speed):
        '''
        Update the speed of the motor where 1 is full forward and
        -1 is full backwards.
        '''
        if speed > 1 or speed < -1:
            raise ValueError( "Speed must be between 1(forward) and -1(reverse)")
        
        self.speed = speed
        self.throttle = int(dk.utils.map_range(abs(speed), -1, 1, -255, 255))
        
        if speed > 0:            
            self.motor.run(self.FORWARD)
        else:
            self.motor.run(self.BACKWARD)
            
        self.motor.setSpeed(self.throttle)
        

    def shutdown(self):
        self.mh.getMotor(self.motor_num).run(Adafruit_MotorHAT.RELEASE)

class Maestro:
    '''
    Pololu Maestro Servo controller
    Use the MaestroControlCenter to set the speed & acceleration values to 0!
    '''
    import threading

    maestro_device = None
    astar_device = None
    maestro_lock = threading.Lock()
    astar_lock = threading.Lock()

    def __init__(self, channel, frequency = 60):
        import serial

        if Maestro.maestro_device == None:
            Maestro.maestro_device = serial.Serial('/dev/ttyACM0', 115200)

        self.channel = channel
        self.frequency = frequency
        self.lturn = False
        self.rturn = False
        self.headlights = False
        self.brakelights = False

        if Maestro.astar_device == None:
            Maestro.astar_device = serial.Serial('/dev/ttyACM2', 115200, timeout= 0.01)

    def set_pulse(self, pulse):
        # Recalculate pulse width from the Adafruit values
        w = pulse * (1 / (self.frequency * 4096)) # in seconds
        w *= 1000 * 1000  # in microseconds
        w *= 4  # in quarter microsenconds the maestro wants
        w = int(w)

        with Maestro.maestro_lock:
            Maestro.maestro_device.write(bytearray([ 0x84,
                                                     self.channel,
                                                     (w & 0x7F),
                                                     ((w >> 7) & 0x7F)]))

    def set_turn_left(self, v):
        if self.lturn != v:
            self.lturn = v
            b = bytearray('L' if v else 'l', 'ascii')
            with Maestro.astar_lock:
                Maestro.astar_device.write(b)

    def set_turn_right(self, v):
        if self.rturn != v:
            self.rturn = v
            b = bytearray('R' if v else 'r', 'ascii')
            with Maestro.astar_lock:
                Maestro.astar_device.write(b)

    def set_headlight(self, v):
        if self.headlights != v:
            self.headlights = v
            b = bytearray('H' if v else 'h', 'ascii')
            with Maestro.astar_lock:
                Maestro.astar_device.write(b)

    def set_brake(self, v):
        if self.brakelights != v:
            self.brakelights = v
            b = bytearray('B' if v else 'b', 'ascii')
            with Maestro.astar_lock:
                Maestro.astar_device.write(b)

    def readline(self):
        ret = None
        with Maestro.astar_lock:
            # expecting lines like
            # E n nnn n
            if Maestro.astar_device.inWaiting() > 8:
                ret = Maestro.astar_device.readline()

        if ret != None:
            ret = ret.rstrip()

        return ret

class Teensy:
    '''
    Teensy Servo controller
    '''
    import threading

    teensy_device = None
    astar_device = None
    teensy_lock = threading.Lock()
    astar_lock = threading.Lock()

    def __init__(self, channel, frequency = 60):
        import serial

        if Teensy.teensy_device == None:
            Teensy.teensy_device = serial.Serial('/dev/teensy', 115200, timeout = 0.01)

        self.channel = channel
        self.frequency = frequency
        self.lturn = False
        self.rturn = False
        self.headlights = False
        self.brakelights = False

        if Teensy.astar_device == None:
            Teensy.astar_device = serial.Serial('/dev/astar', 115200, timeout = 0.01)

    def set_pulse(self, pulse):
        # Recalculate pulse width from the Adafruit values
        w = pulse * (1 / (self.frequency * 4096)) # in seconds
        w *= 1000 * 1000  # in microseconds

        with Teensy.teensy_lock:
            Teensy.teensy_device.write(("%c %.1f\n" % (self.channel, w)).encode('ascii'))

    def set_turn_left(self, v):
        if self.lturn != v:
            self.lturn = v
            b = bytearray('L' if v else 'l', 'ascii')
            with Teensy.astar_lock:
                Teensy.astar_device.write(b)

    def set_turn_right(self, v):
        if self.rturn != v:
            self.rturn = v
            b = bytearray('R' if v else 'r', 'ascii')
            with Teensy.astar_lock:
                Teensy.astar_device.write(b)

    def set_headlight(self, v):
        if self.headlights != v:
            self.headlights = v
            b = bytearray('H' if v else 'h', 'ascii')
            with Teensy.astar_lock:
                Teensy.astar_device.write(b)

    def set_brake(self, v):
        if self.brakelights != v:
            self.brakelights = v
            b = bytearray('B' if v else 'b', 'ascii')
            with Teensy.astar_lock:
                Teensy.astar_device.write(b)

    def teensy_readline(self):
        ret = None
        with Teensy.teensy_lock:
            # expecting lines like
            # E n nnn n
            if Teensy.teensy_device.inWaiting() > 8:
                ret = Teensy.teensy_device.readline()

        if ret != None:
            ret = ret.rstrip()

        return ret

    def astar_readline(self):
        ret = None
        with Teensy.astar_lock:
            # expecting lines like
            # E n nnn n
            if Teensy.astar_device.inWaiting() > 8:
                ret = Teensy.astar_device.readline()

        if ret != None:
            ret = ret.rstrip()

        return ret

class MockController(object):
    def __init__(self):
        pass

    def run(self, pulse):
        pass

    def shutdown(self):
        pass
