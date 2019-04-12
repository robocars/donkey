#!/bin/sh
echo 0 > /sys/devices/system/cpu/cpu0/online
sleep 1
echo 0 > /sys/devices/system/cpu/cpu1/online
sleep 1
echo 0 > /sys/devices/system/cpu/cpu2/online
sleep 1
echo 0 > /sys/devices/system/cpu/cpu3/online

