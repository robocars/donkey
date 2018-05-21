""" 
CAR CONFIG 

This file is read by your car application's manage.py script to change the car
performance. 

EXMAPLE
-----------
import dk
cfg = dk.load_config(config_path='~/d2/config.py')
print(cfg.CAMERA_RESOLUTION)

"""


import os

#PATHS
CAR_PATH = PACKAGE_PATH = os.path.dirname(os.path.realpath(__file__))
DATA_PATH = os.path.join(CAR_PATH, 'data')
MODELS_PATH = os.path.join(CAR_PATH, 'models')

#VEHICLE
DRIVE_LOOP_HZ = 20
MAX_LOOPS = 100000

#CAMERA
USE_WEB_CAMERA = False
CAMERA_RESOLUTION = (90, 160) #(height, width)
CAMERA_FRAMERATE = DRIVE_LOOP_HZ

#TX
USE_TX_AS_DEFAULT = False
TX_THROTTLE_MIN = 913
TX_THROTTLE_MAX = 2111
TX_STEERING_MIN = 960
TX_STEERING_MAX = 2060
TX_THROTTLE_TRESH = 1470
TX_CH_AUX_TRESH = 1500
TX_VERBOSE  = False

#THROTTLEINLINE
USE_THROTTLEINLINE = False
THROTTLEINLINE_ANGLE_MIN = 30
THROTTLEINLINE_ANGLE_MAX = 95
THROTTLEINLINE_BOOST_FACTOR = 1.5

USE_PWM_ACTUATOR = True
#STEERING
STEERING_CHANNEL = 1
#STEERING_AMPLITUDE = 100
#STEERING_LEFT_PWM = 369+STEERING_AMPLITUDE
#STEERING_RIGHT_PWM = 369-STEERING_AMPLITUDE
STEERING_LEFT_PWM = ((TX_STEERING_MAX)/(16666/4095))
STEERING_RIGHT_PWM =((TX_STEERING_MIN)/(16666/4095))

#THROTTLE
THROTTLE_CHANNEL = 0
THROTTLE_FORWARD_PWM = 410
THROTTLE_STOPPED_PWM = 384
THROTTLE_REVERSE_PWM = 310

#TRAINING
BATCH_SIZE = 128
TRAIN_TEST_SPLIT = 0.8

#JOYSTICK
USE_JOYSTICK_AS_DEFAULT = False
JOYSTICK_MAX_THROTTLE = 0.25
JOYSTICK_STEERING_SCALE = 1.0
AUTO_RECORD_ON_THROTTLE = True
JOYSTICK_THROTTLE_AXIS = 'rz'
JOYSTICK_STEERING_AXIS = 'x'
JOYSTICK_DRIVING_MODE_BUTTON = 'trigger'
JOYSTICK_RECORD_TOGGLE_BUTTON = 'circle'
JOYSTICK_INCREASE_MAX_THROTTLE_BUTTON = 'triangle'
JOYSTICK_DECREASE_MAX_THROTTLE_BUTTON = 'cross'
JOYSTICK_INCREASE_THROTTLE_SCALE_BUTTON = 'base'
JOYSTICK_DECREASE_THROTTLE_SCALE_BUTTON = 'top2'
JOYSTICK_INCREASE_STEERING_SCALE_BUTTON = 'base2'
JOYSTICK_DECREASE_STEERING_SCALE_BUTTON = 'pinkie'
JOYSTICK_TOGGLE_CONSTANT_THROTTLE_BUTTON = 'top'
JOYSTICK_VERBOSE = False
