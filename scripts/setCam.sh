#!/bin/sh
# switch to manual exp
v4l2-ctl -d /dev/video0 -c exposure_auto=1
# dark mode
v4l2-ctl -d /dev/video0 -c exposure_absolute=50
#sharpness min=1 max=7 step=1 default=2 value=2
# v4l2-ctl -d /dev/video0 -c sharpness=2
# gama correction min=100 max=300 step=1 default=165 value=165
# v4l2-ctl -d /dev/video0 -c gamma=165
# backlight_compensation min=0 max=1 step=1 default=0 value=0
# v4l2-ctl -d /dev/video0 -c backlight_compensation=0
# white_balance_temperature min=2800 max=6500 step=10 default=4600 value=4600 flags=inactive
# v4l2-ctl -d /dev/video0 -c white_balance_temperature_auto=0
# v4l2-ctl -d /dev/video0 -c white_balance_temperature=3200
