#!/bin/sh
PID=`pidof /usr/bin/python3 manage.py`
echo $PID
kill -10 $PID

