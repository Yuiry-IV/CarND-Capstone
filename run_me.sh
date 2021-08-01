#!/bin/bash
echo "run me"
echo "pip install pillow==6.2.1"
if [ 1 == 1 ]; then
   #cd /home/workspace
   #cd CarND-Capstone
   #pip install -r requirements.txt
   #cd ros
   catkin_make
   source devel/setup.sh
   roslaunch launch/styx.launch
fi
if [ 0 == 1 ]; then
   sudo docker run -p 4567:4567 -v $PWD:/capstone -v /tmp/log:/root/.ros/ --rm -it capstone
fi
