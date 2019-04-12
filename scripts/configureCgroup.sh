#!/bin/sh
#sudo cgdelete -r -g "cpuset:/robocars"
sudo cgcreate -g cpuset:robocars
sudo cgset -r cpuset.cpus='4-5' robocars
sudo cgset -r cpuset.mems='0' robocars
sudo chown -R ${USER} /sys/fs/cgroup/cpuset/robocars
#cgexec -g cpuset:/robocars python3 manage.py drive --model models/model_cat

